/**
 * Canvas 读图：缩放后逐像素返回 RGBA 数据
 */
const ColorExtract = (() => {
  const MAX_SIZE = 512;

  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('图片加载失败'));
      };
      img.src = url;
    });
  }

  function extractPixelsFromImage(img) {
    const scale = Math.min(1, MAX_SIZE / Math.max(img.width, img.height));
    const width = Math.max(1, Math.round(img.width * scale));
    const height = Math.max(1, Math.round(img.height * scale));
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, width, height);
    const { data } = ctx.getImageData(0, 0, width, height);
    const previewUrl = canvas.toDataURL('image/jpeg', 0.85);

    let validPixels = 0;
    for (let i = 3; i < data.length; i += 4) {
      if (data[i] >= 128) validPixels++;
    }

    return { data, width, height, previewUrl, validPixels };
  }

  function extractPixels(file) {
    return loadImage(file).then(extractPixelsFromImage);
  }

  return { extractPixels };
})();
