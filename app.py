import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import io

# --------------------------
# 1. 登录状态管理（极简版）
# --------------------------
def check_login() -> bool:
    """检查是否已登录"""
    return st.session_state.get("logged_in", False)

def login(username: str, password: str) -> bool:
    """明文验证，无任何加密，确保成功"""
    username = username.strip()
    password = password.strip()
    
    # 唯一有效组合，简单直接
    valid_credentials = [
        ("admin", "123456")
    ]
    
    if (username, password) in valid_credentials:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    """退出登录"""
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# --------------------------
# 2. 辅助函数：图片处理
# --------------------------
def load_image(uploaded_file):
    """加载上传的图片，返回OpenCV格式和PIL格式"""
    if uploaded_file is not None:
        # 读取文件为字节流
        bytes_data = uploaded_file.getvalue()
        # 转换为OpenCV格式
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)  # 转换为RGB
        # 转换为PIL格式（Streamlit展示用）
        pil_img = Image.open(io.BytesIO(bytes_data))
        return cv2_img, pil_img
    return None, None

# --------------------------
# 2. 登录页面（无表单，极简版）
# --------------------------
def render_login_page():
    st.set_page_config(page_title="🔒 系统登录", layout="centered")
    st.title("🔒 恶劣天气图像复原系统 - 登录")
    st.markdown("---")

    # 放弃 st.form，直接用输入框+按钮，避免表单缓存问题
    username = st.text_input("用户名", placeholder="请输入用户名")
    password = st.text_input("密码", type="password", placeholder="请输入密码")
    submit_btn = st.button("登录", type="primary", use_container_width=True)

    # 登录逻辑（直接绑定按钮，无表单提交延迟）
    if submit_btn:
        if not username or not password:
            st.error("❌ 用户名或密码不能为空！")
        elif login(username, password):
            st.success(f"✅ 欢迎回来，{st.session_state['username']}！正在进入系统...")
            time.sleep(0.5)
            # 强制刷新页面（兼容所有 Streamlit 版本）
            st.experimental_rerun()
        else:
            st.error("❌ 用户名或密码错误！")

# --------------------------
# 3. 主应用页面（新增双画面图片展示功能）
# --------------------------
def render_main_app():
    st.set_page_config(
        page_title="🌨️ 恶劣天气下基于频域感知的图像复原系统",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with st.sidebar:
        st.title(f"⚙️ 系统配置（{st.session_state['username']}）")
        if st.button("🚪 退出登录", type="secondary", use_container_width=True):
            logout()
            st.experimental_rerun()

        st.markdown("---")
        st.subheader("参数阈值")
        conf_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.40, 0.01)
        iou_threshold = st.slider("IOU阈值", 0.0, 1.0, 0.40, 0.01)

        st.markdown("---")
        st.subheader("输入配置")
        input_mode = st.selectbox("选择输入", ["图像复原"], index=0)
        
        # 新增：支持上传1-2张图片（适配单/双画面）
        uploaded_files = st.file_uploader(
            "上传图像（支持1-2张）",
            type=["jpg", "png", "jpeg"],
            help="支持 JPG/PNG 格式，单文件最大 200MB",
            accept_multiple_files=True  # 允许多文件上传
        )

        st.markdown("---")
        st.subheader("下游任务")
        downstream_task = st.selectbox(
            "选择任务",
            options=["目标检测", "场景分割"],
            index=0,
            help="选择图像复原后的下游处理任务"
        )

    # --------------------------
    # 主界面核心逻辑
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
    # 核心功能：点击开始运行后展示图片
    # --------------------------
    if run_btn:
        # 检查是否上传了图片
        if not uploaded_files:
            st.error("❌ 请先上传至少1张图片！")
        else:
            # 清空默认提示
            placeholder.empty()
            
            # 加载上传的图片
            img_list = []
            for file in uploaded_files[:2]:  # 最多取2张
                cv2_img, pil_img = load_image(file)
                if cv2_img is not None:
                    img_list.append((file.name, pil_img, cv2_img))
            
            # 单画面模式：展示第一张图片
            if display_mode == "单画面":
                if img_list:
                    with placeholder.container():
                        st.subheader("📷 原始图像")
                        st.image(img_list[0][1], caption=img_list[0][0], use_column_width=True)
            # 双画面模式：展示前两张图片（原图像+对比/复原图）
            else:
                with placeholder.container():
                    col_left, col_right = st.columns(2)
                    # 左列：第一张图片（原始恶劣天气图）
                    if len(img_list) >= 1:
                        with col_left:
                            st.subheader("🌧️ 原始恶劣天气图像")
                            st.image(img_list[0][1], caption=img_list[0][0], use_column_width=True)
                    # 右列：第二张图片（参考/复原图）
                    if len(img_list) >= 2:
                        with col_right:
                            st.subheader("✨ 复原后图像")
                            st.image(img_list[1][1], caption=img_list[1][0], use_column_width=True)
                    # 只有1张图片时，右列提示
                    elif len(img_list) == 1:
                        with col_right:
                            st.info("ℹ️ 请上传第二张图片以展示双画面对比")
            
            # 运行成功提示
            st.success("✅ 图片加载完成！")

# --------------------------
# 4. 程序入口（初始化+路由）
# --------------------------
if __name__ == "__main__":
    # 强制初始化 session_state，避免任何缺失
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # 路由控制
    if not check_login():
        render_login_page()
    else:
        render_main_app()
