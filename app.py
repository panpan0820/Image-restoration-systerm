import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import hashlib

# --------------------------
# 1. 配置账户（暂时注释，改用明文）
# --------------------------
# USER_CREDENTIALS = {
#     "admin": "21232f297a57a5a743894a0e4a801fc",
#     "user": "e10adc3949ba59abbe56e057f20f883e"
# }

# def md5(password: str) -> hashlib.md5:
#     """密码加密函数（暂时注释）"""
#     return hashlib.md5(password.encode("utf-8"))

# --------------------------
# 2. 登录状态管理
# --------------------------
def check_login() -> bool:
    """检查是否已登录"""
    return st.session_state.get("logged_in", False)

def login(username: str, password: str) -> bool:
    """验证登录信息（临时改用明文，确保能登录）"""
    # 去除前后空格
    username = username.strip()
    password = password.strip()
    
    # 明文比对（简单直接，100% 不报错）
    if username == "admin" and password == "admin":
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    elif username == "user" and password == "123456":
        st.session_state["username"] = username
        st.session_state["logged_in"] = True
        return True
    else:
        return False

def logout():
    """退出登录"""
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# --------------------------
# 3. 登录页面（未登录时显示）
# --------------------------
def render_login_page():
    st.set_page_config(page_title="🔒 系统登录", layout="centered")
    st.title("🔒 恶劣天气图像复原系统 - 登录")
    st.markdown("---")

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submit_btn = st.form_submit_button("登录", type="primary", use_container_width=True)

    if submit_btn:
        if not username or not password:
            st.error("❌ 用户名或密码不能为空！")
        elif login(username, password):
            st.success(f"✅ 欢迎回来，{username}！正在进入系统...")
            time.sleep(0.5)
            # 兼容旧版本Streamlit
            st.experimental_rerun()  
        else:
            st.error("❌ 用户名或密码错误，请重试！")

# --------------------------
# 4. 主应用页面（已登录时显示）
# --------------------------
def render_main_app():
    st.set_page_config(
        page_title="🌨️ 恶劣天气下基于频域感知的图像复原系统",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --------------------------
    # 侧边栏（含退出登录）
    # --------------------------
    with st.sidebar:
        st.title(f"⚙️ 系统配置（{st.session_state['username']}）")
        # 退出登录按钮（兼容版）
        if st.button("🚪 退出登录", type="secondary", use_container_width=True):
            logout()
            st.experimental_rerun()

        st.markdown("---")
        
        # 参数阈值区
        st.subheader("参数阈值")
        conf_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.40, 0.01)
        iou_threshold = st.slider("IOU阈值", 0.0, 1.0, 0.40, 0.01)

        st.markdown("---")
        
        # 输入配置区
        st.subheader("输入配置")
        input_mode = st.selectbox("选择输入", ["图像复原"], index=0)
        uploaded_file = st.file_uploader(
            "上传图像",
            type=["jpg", "png", "jpeg"],
            help="支持 JPG/PNG 格式，单文件最大 200MB"
        )

        st.markdown("---")
        
        # 下游任务区
        st.subheader("下游任务")
        downstream_task = st.selectbox(
            "选择任务",
            options=["目标检测", "场景分割"],
            index=0,
            help="选择图像复原后的下游处理任务"
        )

    # --------------------------
    # 主界面
    # --------------------------
    st.title("🌨️ 恶劣天气下基于频域感知的图像复原系统")
    st.markdown("---")

    # 控制面板
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        display_mode = st.radio("显示模式", ["单画面", "双画面"], horizontal=True, index=1)
    with col2:
        target_filter = st.selectbox("目标过滤", ["全部目标"], index=0)
    with col3:
        run_btn = st.button("▶️ 开始运行", type="primary", use_container_width=True)

    # 复原画面区
    st.markdown("### 复原画面")
    placeholder = st.empty()

    # 结果表格区
    result_placeholder = st.empty()

    # 默认提示
    with placeholder.container():
        st.info("""
        ✅ 应用已正常启动
        \n📌 新增功能：左侧「输入配置」下方可选择「目标检测」/「场景分割」下游任务
        \n请在左侧上传图像，然后点击【开始运行】按钮。
        """)

    # 动态结果标题
    if downstream_task == "目标检测":
        result_placeholder.markdown("### 🎯 目标检测结果")
    else:
        result_placeholder.markdown("### 🎨 场景分割结果")

# --------------------------
# 5. 程序入口（控制登录流）
# --------------------------
if __name__ == "__main__":
    # 初始化 session_state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None

    # 路由控制：未登录 → 登录页；已登录 → 主应用
    if not check_login():
        render_login_page()
    else:
        render_main_app()
