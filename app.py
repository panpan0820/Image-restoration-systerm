import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# --------------------------
# 1. 页面样式定制（核心：添加天气背景）
# --------------------------
def set_page_style():
    """设置页面样式，添加恶劣天气背景图"""
    st.markdown("""
    <style>
    /* 全局背景：添加雨雪天气纹理，半透明不遮挡内容 */
    .stApp {
        background-image: url("https://picsum.photos/id/1058/1920/1080"); /* 雨天背景图 */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: rgba(255, 255, 255, 0.85); /* 白色遮罩提高可读性 */
        background-blend-mode: overlay;
    }
    /* 登录框容器样式：白色背景+圆角+阴影 */
    .login-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        margin: 0 auto;
    }
    /* 按钮样式优化 */
    .stButton>button {
        background-color: #e63946;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 0;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #d62828;
    }
    /* 输入框样式优化 */
    .stTextInput>div>div>input {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------
# 2. 登录状态管理（保留已修复的极简逻辑）
# --------------------------
def check_login() -> bool:
    return st.session_state.get("logged_in", False)

def login(username: str, password: str) -> bool:
    username = username.strip()
    password = password.strip()
    valid_credentials = [("admin", "123456")]
    if (username, password) in valid_credentials:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# --------------------------
# 3. 登录页面（添加天气背景+美化布局）
# --------------------------
def render_login_page():
    st.set_page_config(page_title="🔒 恶劣天气图像复原系统 - 登录", layout="centered")
    # 应用自定义样式（含天气背景）
    set_page_style()
    
    # 登录容器（带白色背景+圆角，提高可读性）
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔒 恶劣天气图像复原系统")
    st.subheader("用户登录", divider="red")

    # 登录输入框
    username = st.text_input("用户名", placeholder="请输入用户名")
    password = st.text_input("密码", type="password", placeholder="请输入密码")
    submit_btn = st.button("登录", use_container_width=True)

    # 登录逻辑
    if submit_btn:
        if not username or not password:
            st.error("❌ 用户名或密码不能为空！")
        elif login(username, password):
            st.success(f"✅ 欢迎回来，{st.session_state['username']}！正在进入系统...")
            time.sleep(0.5)
            st.experimental_rerun()
        else:
            st.error("❌ 用户名或密码错误！")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# 4. 主应用页面（保留原有功能）
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
        uploaded_file = st.file_uploader(
            "上传图像",
            type=["jpg", "png", "jpeg"],
            help="支持 JPG/PNG 格式，单文件最大 200MB"
        )

        st.markdown("---")
        st.subheader("下游任务")
        downstream_task = st.selectbox(
            "选择任务",
            options=["目标检测", "场景分割"],
            index=0,
            help="选择图像复原后的下游处理任务"
        )

    st.title("🌨️ 恶劣天气下基于频域感知的图像复原系统")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        display_mode = st.radio("显示模式", ["单画面", "双画面"], horizontal=True, index=1)
    with col2:
        target_filter = st.selectbox("目标过滤", ["全部目标"], index=0)
    with col3:
        run_btn = st.button("▶️ 开始运行", type="primary", use_container_width=True)

    st.markdown("### 复原画面")
    placeholder = st.empty()
    result_placeholder = st.empty()

    with placeholder.container():
        st.info("""
        ✅ 应用已正常启动
        \n📌 新增功能：左侧「输入配置」下方可选择「目标检测」/「场景分割」下游任务
        \n请在左侧上传图像，然后点击【开始运行】按钮。
        """)

    if downstream_task == "目标检测":
        result_placeholder.markdown("### 🎯 目标检测结果")
    else:
        result_placeholder.markdown("### 🎨 场景分割结果")

# --------------------------
# 5. 程序入口
# --------------------------
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not check_login():
        render_login_page()
    else:
        render_main_app()
