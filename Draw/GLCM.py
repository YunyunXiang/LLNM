#GLCM特征图可视化
def visualize_glcm_final(image_path):
    img_array = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    
    # --- 改进 1: 自动裁剪中心区域 (避开大量黑色背景) ---
    h, w = img.shape
    cy, cx = h // 2, w // 2
    side = min(h, w) // 3
    # 截取图像中心部分（通常是病灶位置）
    img_crop = img[cy-side:cy+side, cx-side:cx+side]
    img_crop = cv2.resize(img_crop, (128, 128))

    # --- 改进 2: 增强对比度后再提取 ---
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    img_enhanced = clahe.apply(img_crop)

    # 压缩灰度级
    img_reduced = (img_enhanced // 8).astype(np.uint8) 
    glcm = graycomatrix(img_reduced, distances=[1], angles=[0, np.pi/4], levels=32, symmetric=True, normed=True)
    # 融合不同方向的矩阵
    glcm_matrix = np.mean(glcm, axis=(2, 3)) 

    # --- 改进 3: 极致的视觉拉伸 ---
    glcm_viz = glcm_matrix.copy()
    glcm_viz[0, 0] = 0 # 再次屏蔽背景
    
    # 使用百分位数裁剪法：强制让前 5% 的亮值达到饱和，从而拉亮暗部
    v_max = np.percentile(glcm_viz, 99.5) 

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(img_enhanced, cmap='gray')
    plt.title("Cropped ROI core area")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    # vmin/vmax 控制颜色映射范围，让原本微弱的灰度关联“浮现”出来
    im = plt.subplot(1, 2, 2).imshow(glcm_viz, cmap='magma', vmax=v_max)
    #plt.title("GLCM 纹理特征图\n(局部缩放 + 动态范围拉伸)")
    plt.title("GLCM texture feature map")
    plt.xlabel("gray level j")
    plt.ylabel("gray level i")
    plt.colorbar(im)

    plt.tight_layout()
    plt.show()

visualize_glcm_final(file_path)