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
# 4. 登录页面（无表单，极简版）
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
# 5. 主应用页面（新增模型选择+独立检测按钮）
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
        input_mode = st.selectbox("选择输入", options=["本地文件", "设备拍摄"], index=0)
        
        # 新增：支持上传1-2张图片（适配单/双画面）
        uploaded_files = st.file_uploader(
            "上传图像",
            type=["jpg", "png", "jpeg"],
            help="支持 JPG/PNG 格式，单文件最大 200MB",
            accept_multiple_files=True  # 允许多文件上传
        )

        # ① 新增：复原模型选择栏
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

    # 控制面板
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        display_mode = st.radio("显示模式", ["单画面", "双画面"], horizontal=True, index=1)
    with col2:
        target_filter = st.selectbox("目标过滤", ["全部目标"], index=0)
    with col3:
        restore_run_btn = st.button("▶️ 运行复原模型", type="primary", use_container_width=True)

    # 复原画面区（带独立的复原运行按钮）
    st.markdown("### 复原画面")
    restore_placeholder = st.empty()
    # 默认提示
    with restore_placeholder.container():
        st.info("""
        ✅ 应用已正常启动
        \n📌 请在左侧上传图像、选择复原模型，然后点击「运行复原模型」按钮
        \n📌 下游任务可选择目标检测/场景分割，点击对应按钮执行
        """)

    # 下游任务结果区（② 目标检测独立运行按钮）
    if downstream_task == "目标检测":
        # 目标检测标题 + 独立运行按钮（横向布局）
        det_col1, det_col2 = st.columns([8, 2])
        with det_col1:
            st.markdown("### 🎯 目标检测结果")
        with det_col2:
            detect_run_btn = st.button("▶️ 运行目标检测", type="secondary", use_container_width=True)
        detect_placeholder = st.empty()
    else:
        st.markdown("### 🎨 场景分割结果")
        detect_placeholder = st.empty()
        detect_run_btn = None  # 场景分割暂不显示按钮

    # --------------------------
    # 核心功能1：运行复原模型（展示复原后图片）
    # --------------------------
    if restore_run_btn:
        # 检查是否上传了图片
        if not uploaded_files:
            st.error("❌ 请先上传至少1张图片！")
        else:
            # 清空默认提示
            restore_placeholder.empty()
            
            # 加载上传的图片
            img_list = []
            for file in uploaded_files[:2]:  # 最多取2张
                cv2_img, pil_img = load_image(file)
                if cv2_img is not None:
                    # 运行复原模型
                    restored_img = run_restoration_model(pil_img, restoration_model)
                    img_list.append((file.name, restored_img, cv2_img))
            
            # 单画面模式：展示第一张复原后图片
            if display_mode == "单画面":
                if img_list:
                    with restore_placeholder.container():
                        st.subheader(f"📷 复原后图像（{restoration_model}）")
                        st.image(img_list[0][1], caption=img_list[0][0], use_column_width=True)
            # 双画面模式：展示原始图+复原后图
            else:
                with restore_placeholder.container():
                    col_left, col_right = st.columns(2)
                    # 左列：原始图片
                    if len(img_list) >= 1:
                        with col_left:
                            st.subheader("🌧️ 原始恶劣天气图像")
                            # 重新加载原始图（未复原）
                            orig_cv2, orig_pil = load_image(uploaded_files[0])
                            st.image(orig_pil, caption=uploaded_files[0].name, use_column_width=True)
                    # 右列：复原后图片
                    if len(img_list) >= 1:
                        with col_right:
                            st.subheader(f"✨ 复原后图像（{restoration_model}）")
                            st.image(img_list[0][1], caption=uploaded_files[0].name, use_column_width=True)
                    # 上传2张图时的补充展示
                    if len(img_list) >= 2:
                        st.info("ℹ️ 已上传2张图片，当前展示第一张的复原效果")
            
            # 运行成功提示
            st.success(f"✅ {restoration_model} 运行完成！")

    # --------------------------
    # 核心功能2：运行目标检测（独立按钮）
    # --------------------------
    if detect_run_btn and downstream_task == "目标检测":
        # 检查是否有复原后的图片/上传的图片
        if not uploaded_files:
            st.error("❌ 请先上传图片并运行复原模型！")
        else:
            detect_placeholder.empty()
            # 加载第一张图片并运行检测
            cv2_img, pil_img = load_image(uploaded_files[0])
            if cv2_img is not None:
                # 运行目标检测模型
                detected_img = run_detection_model(pil_img)
                with detect_placeholder.container():
                    st.subheader("🔍 目标检测结果展示")
                    st.image(detected_img, caption="目标检测后图像", use_column_width=True)
                    st.success("✅ 目标检测运行完成！")

# --------------------------
# 6. 程序入口（初始化+路由）
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
