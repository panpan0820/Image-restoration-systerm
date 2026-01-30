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
# 3. 模拟模型处理函数（占位，可替换为真实逻辑）
# --------------------------
def run_restoration_model(img, model_name):
    """模拟图像复原模型处理"""
    st.info(f"🔧 正在使用【{model_name}】进行图像复原...")
    time.sleep(1)
    # 这里仅返回原图作为占位，实际可替换为真实复原逻辑
    return img

def run_detection_model(img):
    """模拟目标检测模型处理"""
    st.info(f"🔍 正在进行目标检测...")
    time.sleep(1)
    # 这里仅返回原图作为占位，实际可替换为真实检测逻辑（如画框、标注）
    return img

# --------------------------
# 4. 自定义样式：统一按钮样式+对齐布局
# --------------------------
def set_custom_style():
    st.markdown("""
    <style>
    /* 统一红色按钮样式 */
    .stButton>button {
        background-color: #e63946 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 0 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background-color: #d62828 !important;
    }
    /* 修复选择框和按钮的对齐问题 */
    .stSelectbox, .stRadio {
        margin-top: 0.5rem !important;
    }
    /* 统一容器间距 */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------
# 5. 登录页面（无表单，极简版）
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
# 6. 主应用页面（双画面固定显示前两张上传图）
# --------------------------
def render_main_app():
    st.set_page_config(
        page_title="🌨️ 恶劣天气下基于频域感知的图像复原系统",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用自定义样式
    set_custom_style()

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
        input_mode = st.selectbox("选择输入", options=["本地文件", "设备拍摄"], index=0)
        
        # 支持上传多张图片（重点：至少2张用于双画面）
        uploaded_files = st.file_uploader(
            "上传图像（双画面需至少上传2张）",
            type=["jpg", "png", "jpeg"],
            help="支持 JPG/PNG 格式，单文件最大 200MB，双画面模式下前两张分别显示在左右侧",
            accept_multiple_files=True
        )

        # 复原模型选择栏
        st.markdown("---")
        st.subheader("复原模型选择")
        restoration_model = st.selectbox(
            "选择图像复原算法",
            options=["去雨模型", "去雾模型", "去雪模型", "通用恶劣天气复原模型"],
            index=0,
            help="不同模型适配不同类型的恶劣天气图像复原"
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

    # 控制面板：调整列宽，确保按钮和下拉框垂直对齐
    col1, col2, col3 = st.columns([1, 1.2, 1.8])
    with col1:
        display_mode = st.radio("显示模式", ["单画面", "双画面"], horizontal=True, index=1)
    with col2:
        target_filter = st.selectbox("目标过滤", ["全部目标"], index=0)
    with col3:
        restore_run_btn = st.button("▶️ 运行复原模型", use_container_width=True)

    # 复原画面区
    st.markdown("### 复原画面")
    restore_placeholder = st.empty()
    # 默认提示
    with restore_placeholder.container():
        st.info("""
        ✅ 应用已正常启动
        \n📌 下游任务可选择目标检测/场景分割，点击对应按钮执行
        """)

    # 下游任务结果区
    if downstream_task == "目标检测":
        # 目标检测标题 + 独立运行按钮
        det_col1, det_col2 = st.columns([8, 2])
        with det_col1:
            st.markdown("### 🎯 目标检测结果")
        with det_col2:
            detect_run_btn = st.button("▶️ 运行目标检测", use_container_width=True)
        detect_placeholder = st.empty()
    else:
        st.markdown("### 🎨 场景分割结果")
        detect_placeholder = st.empty()
        detect_run_btn = None

    # --------------------------
    # 核心功能1：运行复原模型（双画面固定显示前两张上传图）
    # --------------------------
    if restore_run_btn:
        # 检查是否上传了图片
        if not uploaded_files:
            st.error("❌ 请先上传图片！")
        else:
            restore_placeholder.empty()
            
            # 加载所有上传的图片（仅取前2张）
            img_list = []
            for idx, file in enumerate(uploaded_files[:2]):  # 仅处理前2张
                cv2_img, pil_img = load_image(file)
                if cv2_img is not None:
                    # 可选：对图片运行复原模型（保留模型功能）
                    restored_img = run_restoration_model(pil_img, restoration_model)
                    img_list.append({
                        "name": file.name,
                        "original": pil_img,
                        "restored": restored_img,
                        "index": idx + 1  # 图片序号（1/2）
                    })
            
            # 单画面模式：显示第一张图片（复原后）
            if display_mode == "单画面":
                if img_list:
                    with restore_placeholder.container():
                        st.subheader(f"📷 第1张图像（{restoration_model}复原后）")
                        st.image(img_list[0]["restored"], caption=img_list[0]["name"], use_column_width=True)
                else:
                    st.warning("⚠️ 未加载到有效图片！")
            
            # 双画面模式：左侧=第1张，右侧=第2张（固定顺序）
            else:
                with restore_placeholder.container():
                    col_left, col_right = st.columns(2)
                    
                    # 左列：固定显示第1张图片
                    if len(img_list) >= 1:
                        with col_left:
                            st.subheader(f"📷 第1张图像（{restoration_model}复原前）")
                            st.image(img_list[0]["restored"], caption=img_list[0]["name"], use_column_width=True)
                    else:
                        with col_left:
                            st.warning("⚠️ 未加载到图片！")
                    
                    # 右列：固定显示第2张图片
                    if len(img_list) >= 2:
                        with col_right:
                            st.subheader(f"📷 第2张图像（{restoration_model}复原后）")
                            st.image(img_list[1]["restored"], caption=img_list[1]["name"], use_column_width=True)
                    else:
                        with col_right:
                            st.error("❌ 请上传退化图片！")
            
            # 运行成功提示
            st.success(f"✅ {restoration_model} 运行完成！共加载 {len(img_list)} 张图片")

    # --------------------------
    # 核心功能2：运行目标检测
    # --------------------------
    if detect_run_btn and downstream_task == "目标检测":
        if not uploaded_files:
            st.error("❌ 请先上传图片并运行复原模型！")
        else:
            detect_placeholder.empty()
            # 加载第一张图片运行检测
            cv2_img, pil_img = load_image(uploaded_files[0])
            if cv2_img is not None:
                detected_img = run_detection_model(pil_img)
                with detect_placeholder.container():
                    st.subheader("🔍 目标检测结果展示（第1张图）")
                    st.image(detected_img, caption=uploaded_files[0].name, use_column_width=True)
                    st.success("✅ 目标检测运行完成！")

# --------------------------
# 7. 程序入口
# --------------------------
if __name__ == "__main__":
    # 初始化session_state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # 路由控制
    if not check_login():
        render_login_page()
    else:
        render_main_app()

