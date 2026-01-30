import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(
    page_title="🌨️ 恶劣天气下基于频域感知的图像复原系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# 侧边栏（调整后：参数阈值 → 输入配置 → 下游任务）
# --------------------------
with st.sidebar:
    st.title("⚙️ 系统配置")
    
    # 1. 参数阈值区（最上方）
    st.subheader("参数阈值")
    conf_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.40, 0.01)
    iou_threshold = st.slider("IOU阈值", 0.0, 1.0, 0.40, 0.01)

    st.markdown("---")  # 分割线
    
    # 2. 输入配置区（中间）
    st.subheader("输入配置")
    input_mode = st.selectbox("选择输入", ["图像复原"], index=0)
    uploaded_file = st.file_uploader(
        "上传图像",
        type=["jpg", "png", "jpeg"],
        help="支持 JPG/PNG 格式，单文件最大 200MB"
    )

    st.markdown("---")  # 分割线
    
    # 3. 下游任务区（最下方，新增！）
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

# 结果表格区（根据下游任务动态显示标题）
result_placeholder = st.empty()

# --------------------------
# 默认提示（无检测逻辑，避免报错）
# --------------------------
with placeholder.container():
    st.info("""
    ✅ 应用已正常启动
    \n📌 新增功能：左侧「输入配置」下方可选择「目标检测」/「场景分割」下游任务
    \n请在左侧上传图像，然后点击【开始运行】按钮。
    """)

# 根据选择的下游任务，显示不同的结果标题
if downstream_task == "目标检测":
    result_placeholder.markdown("### 🎯 目标检测结果")
else:
    result_placeholder.markdown("### 🎨 场景分割结果")

