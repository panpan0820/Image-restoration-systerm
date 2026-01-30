import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# --------------------------
# 1. 页面样式定制（彻底屏蔽白框+完整天气背景）
# --------------------------
def set_page_style():
    """设置页面样式，强制隐藏所有无关空白元素"""
    st.markdown("""
    <style>
    /* 1. 彻底重置所有样式，消除任何默认空白 */
    * {
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box !important;
    }
    /* 2. 页面主体：全屏天气背景，无任何留白 */
    .stApp {
        background-image: url("https://picsum.photos/id/1058/1920/1080"); /* 雨天背景 */
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
        background-color: rgba(255, 255, 255, 0.85) !important;
        background-blend-mode: overlay !important;
        height: 100vh !important;  /* 全屏高度 */
        width: 100vw !important;   /* 全屏宽度 */
        overflow: hidden !important; /* 隐藏滚动条，避免空白 */
    }
    /* 3. 强制隐藏所有无关的空白元素（关键：消除红框内的白框） */
    .stApp > div:first-child,  /* 顶部空白容器 */
    .stApp > div:nth-child(2), /* 调试占位元素 */
    [data-testid="stHeader"],  /* Streamlit 顶部标题栏 */
    [data-testid="stToolbar"], /* 右上角工具栏 */
    [data-testid="stDecoration"] /* 装饰性空白元素 */
    {
        display: none !important;  /* 强制隐藏 */
        height: 0 !important;
        width: 0 !important;
    }
    /* 4. 登录框容器：居中+纯白背景+阴影，完全隔离 */
    .login-container {
        background-color: rgba(255, 255, 255, 0.98) !important;
        padding: 3rem !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
        max-width: 480px !important;
        margin: 10vh auto !important;  /* 垂直居中 */
        z-index: 9999 !important;      /* 置顶显示 */
    }
    /* 5. 输入框/按钮样式优化 */
    .stTextInput>div>div>input {
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 16px !important;
        margin-bottom: 1rem !important;
    }
    .stButton>button {
        background-color: #dc2626 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }
    .stButton>button:hover {
        background-color: #b91c1c !important;
    }
    /* 6. 标题样式 */
    h1 {
        color: #1f2937 !important;
        font-size: 24px !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    .stSubheader {
        color: #4b5563 !important;
        font-size: 18px !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    /* 7. 提示文字样式 */
    .stError, .stSuccess {
        text-align: center !important;
        margin-top: 1rem !important;
        font-size: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------
# 2. 登录状态管理（保留极简逻辑）
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
# 3. 登录页面（彻底无白框）
# --------------------------
def render_login_page():
    # 关键：禁用所有默认组件，避免生成空白元素
    st.set_page_config(
        page_title="🔒 恶劣天气图像复原系统 - 登录", 
        layout="wide",  # 改为wide，避免centered布局的默认空白
        initial_sidebar_state="collapsed",
        menu_items=None  # 禁用右上角菜单
    )
    # 应用自定义样式（核心：隐藏所有无关元素）
    set_page_style()
    
    # 登录容器（唯一显示的内容）
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔒 恶劣天气图像复原系统")
    st.subheader("用户登录", divider="red")

    # 登录输入框
    username = st.text_input("用户名", placeholder="请输入 admin 或 user")
    password = st.text_input("密码", type="password", placeholder="admin 或 123456")
    submit_btn = st.button("登录")

    # 登录逻辑
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
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not check_login():
        render_login_page()
    else:
        render_main_app()
