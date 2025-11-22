import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
from pathlib import Path
import torchvision.models as models
from torchvision import transforms
from typing import List, Optional

# Configuração
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMG_SIZE = 224

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
ENSEMBLE_MODELS_DIR = BASE_DIR / "model" / "ensemble_models2"

# Labels do Modelo vs IDs do App
MODEL_EMOTIONS = ["Raiva", "Nojo", "Medo", "Feliz", "Triste", "Surpresa", "Neutro"]
APP_MOOD_IDS = {
    "Raiva": "angry",
    "Nojo": "disgust",
    "Medo": "fear",
    "Feliz": "happy",
    "Triste": "sad",
    "Surpresa": "surprise",
    "Neutro": "neutral"
}

##################################
# MODELO (Portado de test_fer_ensemble.py)
##################################

class SEBlock(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.squeeze(x).view(b, c)
        y = self.excitation(y).view(b, c, 1, 1)
        return x * y.expand_as(x)

class SEResNet34Improved(nn.Module):
    def __init__(self, num_classes=7, dropout=0.3):
        super().__init__()
        resnet = models.resnet34(weights=None)
        
        self.conv1 = resnet.conv1
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool
        
        self.layer1 = nn.Sequential(resnet.layer1, SEBlock(64))
        self.layer2 = nn.Sequential(resnet.layer2, SEBlock(128))
        self.layer3 = nn.Sequential(resnet.layer3, SEBlock(256))
        self.layer4 = nn.Sequential(resnet.layer4, SEBlock(512))
        
        self.avgpool = resnet.avgpool
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(256),
            nn.Dropout(dropout * 0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

##################################
# SINGLETON PARA MODELOS
##################################

class MoodDetectorService:
    _instance = None
    _models: List[nn.Module] = []
    _face_detector = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MoodDetectorService, cls).__new__(cls)
        return cls._instance

    def _load_models(self):
        if self._models:
            return

        print(f"📦 Carregando modelos de: {ENSEMBLE_MODELS_DIR}")
        model_files = sorted(list(ENSEMBLE_MODELS_DIR.glob("model_*.pth")))
        
        if not model_files:
            print(f"❌ Nenhum modelo encontrado em {ENSEMBLE_MODELS_DIR}")
            return

        for model_path in model_files:
            try:
                model = SEResNet34Improved(num_classes=7, dropout=0.3).to(DEVICE)
                model.load_state_dict(torch.load(str(model_path), map_location=DEVICE))
                model.eval()
                self._models.append(model)
                print(f"✓ Modelo carregado: {model_path.name}")
            except Exception as e:
                print(f"❌ Erro ao carregar {model_path.name}: {e}")

        # Carrega detector de face
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        
        # [FIX WINDOWS PATH ENCODING ISSUE]
        # OpenCV C++ implementation struggles with non-ascii characters in paths on Windows.
        # Workaround: Copy the xml file to a temporary directory with a safe path.
        import tempfile
        import shutil

        if os.name == 'nt':  # Windows
            try:
                # Create a temporary file with .xml extension
                temp_dir = tempfile.gettempdir() # Usually C:\Users\User\AppData\Local\Temp or similar
                temp_cascade_path = os.path.join(temp_dir, "haarcascade_frontalface_default_temp.xml")
                
                if os.path.exists(cascade_path):
                    print(f"🔄 Copiando haarcascade para caminho seguro: {temp_cascade_path}")
                    shutil.copy2(cascade_path, temp_cascade_path)
                    cascade_path = temp_cascade_path
                else:
                    # Fallback logic if original path not found directly
                     cv2_base_dir = os.path.dirname(cv2.__file__)
                     possible_paths = [
                        os.path.join(cv2_base_dir, "data", "haarcascade_frontalface_default.xml"),
                        os.path.join(cv2_base_dir, "..", "data", "haarcascade_frontalface_default.xml"),
                    ]
                     for p in possible_paths:
                        if os.path.exists(p):
                            print(f"🔄 Copiando haarcascade (fallback) para caminho seguro: {temp_cascade_path}")
                            shutil.copy2(p, temp_cascade_path)
                            cascade_path = temp_cascade_path
                            break
            except Exception as e:
                print(f"⚠ Erro ao tentar copiar haarcascade para temp: {e}")
        
        if not os.path.exists(cascade_path):
            print(f"⚠ Aviso: Haarcascade não encontrado em {cascade_path}")
            # Tenta encontrar no diretório do pacote cv2 (se não tiver sido sobrescrito pelo workaround acima ou falhou)
            cv2_base_dir = os.path.dirname(cv2.__file__)
            possible_paths = [
                os.path.join(cv2_base_dir, "data", "haarcascade_frontalface_default.xml"),
                os.path.join(cv2_base_dir, "..", "data", "haarcascade_frontalface_default.xml"),  # as vezes fica fora
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    cascade_path = p
                    break
        
        print(f"🔍 Carregando detector de face de: {cascade_path}")
        self._face_detector = cv2.CascadeClassifier(cascade_path)

        if self._face_detector.empty():
            print(f"❌ ERRO CRÍTICO: Falha ao carregar CascadeClassifier de {cascade_path}")
            # Cria um detector dummy para não crashar imediatamente, mas vai falhar no uso
            # O ideal é tratar isso no loop principal checking if empty


    def _preprocess_face(self, face_gray):
        face_resized = cv2.resize(face_gray, (IMG_SIZE, IMG_SIZE))
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_GRAY2RGB)
        face_normalized = face_rgb.astype("float32") / 255.0
        
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return transform(face_normalized).unsqueeze(0).to(DEVICE)

    def _predict(self, face_tensor):
        if not self._models:
            return None

        all_probs = []
        with torch.no_grad():
            for model in self._models:
                # TTA simples (Flip)
                pred_normal = F.softmax(model(face_tensor), dim=1)
                pred_flip = F.softmax(model(torch.flip(face_tensor, dims=[3])), dim=1)
                avg_pred = (pred_normal + pred_flip) / 2
                all_probs.append(avg_pred.cpu().numpy()[0])
        
        final_probs = np.array(all_probs).mean(axis=0)
        return final_probs

    def open_camera_and_detect(self) -> Optional[str]:
        """
        Abre a câmera, mostra detecção e retorna o ID do mood detectado ao pressionar SPACE/ENTER.
        """
        self._load_models()
        if not self._models:
            print("Nenhum modelo disponível para detecção.")
            return None

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Não foi possível abrir a webcam.")
            return None

        if self._face_detector.empty():
             print("❌ Detector de face não foi carregado corretamente. Verifique a instalação do opencv-python.")
             return None

        detected_mood_id = None
        frame_count = 0
        current_emotion = "Aguardando..."
        current_conf = 0.0
        
        print("🎥 Câmera iniciada. Pressione ESPAÇO ou ENTER para confirmar o mood.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Processa a cada 3 frames para performance
            if frame_count % 3 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self._face_detector.detectMultiScale(gray, 1.2, 5)

                # Se houver faces, pega a maior (mais próxima)
                if len(faces) > 0:
                    # Ordena por área (w * h), pega o maior
                    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
                    x, y, w, h = faces[0]
                    
                    face_gray = gray[y:y+h, x:x+w]
                    face_tensor = self._preprocess_face(face_gray)
                    probs = self._predict(face_tensor)
                    
                    pred_idx = np.argmax(probs)
                    emotion_label = MODEL_EMOTIONS[pred_idx]
                    current_conf = probs[pred_idx] * 100
                    current_emotion = emotion_label
                    detected_mood_id = APP_MOOD_IDS.get(emotion_label, "neutral")

                    # Desenha retângulo
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Texto
                    label = f"{emotion_label} {current_conf:.0f}%"
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Instruções na tela
            cv2.putText(frame, "Pressione ESPACO para confirmar", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Moodify - Deteccao de Emocao", frame)

            key = cv2.waitKey(1) & 0xFF
            # Space (32) or Enter (13)
            if key == 32 or key == 13:
                if detected_mood_id:
                    print(f"Mood confirmado: {current_emotion} ({detected_mood_id})")
                    break
                else:
                    print("Nenhum rosto detectado para confirmar.")
            
            # 'q' ou ESC para sair sem selecionar
            if key == ord('q') or key == 27:
                detected_mood_id = None
                break
            
            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()
        return detected_mood_id

# Instância global para ser importada
mood_detector = MoodDetectorService()

