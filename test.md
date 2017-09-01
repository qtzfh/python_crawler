# 肺结节数据处理、训练过程的方法分析


------

### 数据预处理
* 读取一个病人下多个dicom文件（ct图片）,获取dicom文件的详细信息：
    * Pixel Spacing：相邻像素点中心的距离
    * Slice Thicknes：扫描层厚
    * Image Orientation：病人左手、头部位置等 
    * Rescale Intercept： 灰度偏移值
    * Slope：像素变化参数
    * ………
* 根据上一项的灰度偏移值、像素变化参数得到真实CT值：
    * 具体公式为：Hu（第i个像素的CT值）=pixel_val（第i个参数的灰度值）*rescale_slope（灰度偏移值）+rescale_intercept（灰度偏移值）
* 将dicom图像中进行侵蚀运算、闭合运算等填充
* 最终生成入下图所示
<figure class="half">
    <img src="http://otqlgqb8g.bkt.clouddn.com/17-9-1/20936627.jpg" width="200" height="200">
    <img src="http://otqlgqb8g.bkt.clouddn.com/17-9-1/4768848.jpg" width="200" height="200">
</figure>

