# Kasina_AIO

## 개요
카시나 선착순 구매 봇입니다. 카시나 AIO는 실시간 재고 추적과 자동 구매 기능을 제공합니다.

## 기술 스택
- **언어**: Python
- **라이브러리**: Selenium, requests, Tesseract OCR
- **결제 시스템**: Selenium을 이용한 자동화 네이버페이 결제
- **OCR**: Tesseract를 사용한 결제 이미지 인식
- **웹 스크래핑**: requests를 이용한 자동화 스크래핑

## 주요 기능
1. 실시간 재고 추적
2. 네이버페이 결제를 위한 Tesseract OCR 필요
3. 네이버 계정 연동 필수 (최초 실행 시)

## 설치 및 실행 방법
1. **Tesseract 설치**: 네이버페이 결제를 위해 OCR을 사용하므로, Tesseract가 필요합니다. Tesseract를 설치하려면 [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract)를 참고하세요.
   
2. **네이버 계정 연동**: 최초 실행 시, 네이버 계정 정보를 입력해야 합니다.

## 사용법
1. `main.py` 파일을 실행합니다.
2. 상품이 입고되면 자동으로 구매가 진행됩니다.

## 주의사항
- 이 봇은 교육 목적으로 제작되었으며, 상업적 사용을 금지합니다.
