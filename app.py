import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# --------------------------
# 1. 页面样式定制（温和修复白框，保留登录界面）
# --------------------------
def set_page_style():
    """温和修复白框，不隐藏核心内容"""
    st.markdown("""
    <style>
    /* 1. 重置默认边距，消除顶部白框 */
    .stApp {
        background-image: url("https://picsum.photos/id/1058/1920/1080"); /* 雨天背景 */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-color: rgba(255, 255, 255, 0.85);
        background-blend-mode: overlay;
        padding-top: 2rem !important;  /* 少量顶部内边距，避免内容顶到边缘 */
        padding-bottom: 2rem !important;
    }
    /* 2. 只隐藏Streamlit默认的顶部空白装饰元素（消除红框白框） */
    [data-testid="stDecoration"],
    [data-testid="stToolbar"] > div:first-child  /* 只隐藏多余的工具栏空白 */
    {
        display: none !important;
    }
    /* 3. 登录框容器：居中+纯白背景+阴影 */
    .login-container {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        max-width: 450px;
        margin: 0 auto;  /* 水平居中 */
    }
    /* 4. 输入框/按钮样式优化 */
    .stTextInput>div>div>input {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.8rem;
        font-size: 15px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #e63946;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 0;
        font-size: 16px;
        font-weight: 500;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #d62828;
    }
    /* 5. 标题样式 */
    h1, .stSubheader {
        text-align: center;
        color: #2b2d42;
    }
    .stSubheader {
        margin-bottom: 1.5rem !important;
    }
    /* 6. 提示文字样式 */
    .stError, .stSuccess {
        text-align: center;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------
# 2. 登录状态管理（极简逻辑，确保登录可用）
# --------------------------
def check_login() -> bool:
    return st.session_state.get("logged_in", False)

def login(username: str, password: str) -> bool:
    username = username.strip()
    password = password.strip()
    valid_credentials = [("admin", "admin"), ("user", "123456")]
    if (username, password) in valid_credentials:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# --------------------------
# 3. 登录页面（正常显示+无白框）
# --------------------------
def render_login_page():
    st.set_page_config(
        page_title="🔒 恶劣天气图像复原系统 - 登录", 
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    # 应用样式（温和修复，不隐藏登录框）
    set_page_style()
    
    # 登录容器（正常显示）
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔒 恶劣天气图像复原系统")
    st.subheader("用户登录", divider="red")

    # 登录输入框（正常显示）
    username = st.text_input("用户名", placeholder="请输入 admin 或 user")
    password = st.text_input("密码", type="password", placeholder="admin 或 123456")
    submit_btn = st.button("登录")

    # 登录逻辑（正常生效）
    if submit_btn:
        if not username or not password:
            st.error("❌ 用户名或密码不能为空！")
        elif login(username, password):
            st.success(f"✅ 欢迎回来，{st.session_state['username']}！正在进入系统...")
            time.sleep(0.5)
            st.experimental_rerun()
        else:
            st.error("❌ 用户名或密码错误！正确组合：admin/admin 或 user/123456")
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
    # 初始化session_state，避免缺失
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # 路由控制：未登录显示登录页，已登录显示主页面
    if not check_login():
        render_login_page()
    else:
        render_main_app()
