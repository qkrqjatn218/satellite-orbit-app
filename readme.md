# 🛰️ Satellite Orbit Propagation Studio

해당 웹 앱은 TLE 데이터를 사용하여 위성 궤도의 궤적, 시각화 및 분석에 활용할 수 있습니다. 

## 🔧 Features
- CelesTrak TLE data integration
- SGP4 & numerical propagation models (RK4, Encke, etc.)
- 3D orbit visualization (Plotly)
- Ground Track mapping
- Altitude & velocity periodicity analysis
- Exportable CSV results

## 📦 Built With
- `streamlit`
- `numpy`, `pandas`
- `plotly`, `astropy`

## 🚀 Getting Started
```bash
git clone https://github.com/qkrqjatn218/satellite-orbit-app.git
cd satellite-orbit-app
pip install -r requirements.txt
streamlit run app.py
```

```
/project
│   home.py                         # 메인 진입점 - 로그인
│   app.py                          # 앱 실행 시작점 - 로그인 로직    
|
├── Reports/
│   │   └── propagation.py          # 궤도 전파 설정                 
|   |   └── results.py              # 결과 시각화   
├── Tool/
│   │   └── search.py               # TLE 검색 및 선택
|   |   └──
├── source/                         # 모델
│       └── SGP4                    # SGP4 모델 코드
│
├── image/
│       └── image.jpg
```

## 🌐 Live Demo
Once deployed, your app will be available at:
```
https://satellite-orbit-app-ggufidwlvysrm9vciq7uwj.streamlit.app/
```

## 🧠 Developer
**Beomsu Park**

## 📄 License
This project is licensed under the MIT License.
