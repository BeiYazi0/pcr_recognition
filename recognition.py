import aiohttp
import io
import os
import numpy as np

from tensorflow.keras.models import load_model

from PIL import Image

from .pcr_res import desc_info


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


_dir = os.path.dirname(__file__)
pcr_model_file = os.path.join(_dir,'models\\pcr_recognition.h5')
pcr_model = load_model(pcr_model_file)


async def download(url):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                content = await resp.read()
                return content
    except:
        return False


async def predict(url, model):
    content = await download(url)
    if not content:
        return []
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGB")
    img = img.resize((224, 224))
    data = np.zeros((1,224, 224, 3), dtype = 'uint8')
    data[0] = np.array(img)
    pred_labels = model.predict(data)
    return pred_labels[0]


async def pcr_matching(url: str): 
    pred_labels = await predict(url, pcr_model)
    if pred_labels == []:
        return '图片下载失败'
    idx = np.argmax(pred_labels)
    p = np.max(pred_labels)
    forward_msg = desc_info(idx, p)
    return forward_msg
        
