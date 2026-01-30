import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import tempfile
import os

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(
    page_title="恶劣天气自动驾驶目标检测",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------
# 加载模型（关键：云环境必须用相对路径）
# --------------------------
@st.cache_resource(show_spinner="正在加载YOLO模型...")
def load_model():
    # 确保你的模型文件叫这个名字，并且和app.py在同目录
    model = YOLO("driving-yolov8n.pt")
    return model


model = load_model()

# --------------------------
# 侧边栏
# --------------------------
with st.sidebar:
    st.title("⚙️ 系统配置")

    st.subheader("参数阈值")
    conf_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.25, 0.01)
    iou_threshold = st.slider("IOU阈值", 0.0, 1.0, 0.5, 0.01)

    st.subheader("📷 输入配置")
    input_mode = st.selectbox("选择输入", ["图片检测", "视频检测"])
    uploaded_file = st.file_uploader(
        f"上传{input_mode[:2]}",
        type=["jpg", "png", "jpeg"] if input_mode == "图片检测" else ["mp4", "avi", "mov"]
    )

# --------------------------
# 主界面
# --------------------------
st.title("🚗 基于YOLOv8的自动驾驶目标检测系统")
st.markdown("---")

# 控制面板
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    display_mode = st.radio("显示模式", ["单画面", "双画面"], horizontal=True)
with col2:
    target_filter = st.selectbox("目标过滤", ["全部目标", "车辆", "行人", "交通标志"])
with col3:
    run_btn = st.button("▶️ 开始运行", type="primary", use_container_width=True)

# 画面展示区
st.markdown("### 检测画面")
placeholder = st.empty()  # 用于动态更新画面

# 结果表格区
result_placeholder = st.empty()

# --------------------------
# 检测逻辑
# --------------------------
if run_btn and uploaded_file is not None:
    with st.spinner("正在处理..."):
        # 处理图片
        if input_mode == "图片检测":
            # 读取上传的图片
            image = Image.open(uploaded_file).convert('RGB')
            img_np = np.array(image)

            # 模型推理
            results = model(
                img_np,
                conf=conf_threshold,
                iou=iou_threshold,
                verbose=False
            )

            # 绘制检测框
            res_plotted = results[0].plot()
            res_plotted = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)  # 转换颜色通道

            # 显示画面
            if display_mode == "单画面":
                placeholder.image(res_plotted, caption="检测结果", use_column_width=True)
            else:
                # 用列对象替代 container，减少 DOM 操作
                col1, col2 = st.columns(2)
                col1.image(image, caption="原始图片", use_column_width=True)
                col2.image(res_plotted, caption="检测结果", use_column_width=True)

            # 生成结果表格
            boxes = results[0].boxes
            table_data = []
            for box in boxes:
                cls_name = model.names[int(box.cls)]
                # 过滤目标（简单实现）
                if target_filter != "全部目标" and not target_filter in cls_name:
                    continue
                conf = float(box.conf)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                table_data.append([
                    cls_name,
                    f"({int(x1)}, {int(y1)})-({int(x2)}, {int(y2)})",
                    f"{conf:.2f}"
                ])

            with result_placeholder.container():
                st.markdown("### 📊 识别结果")
                st.dataframe(
                    table_data,
                    column_names=["类别", "位置", "置信度"],
                    use_container_width=True
                )

        # 处理视频（可选功能）
        else:
            st.warning("视频检测功能在免费版云端可能因资源限制卡顿，建议本地运行。")

else:
    # 默认显示封面图
    with placeholder.container():

        st.info("请在左侧上传图片或视频，然后点击【开始运行】按钮。")
