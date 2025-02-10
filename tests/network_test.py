import sys
import json
from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtNetwork import (QNetworkAccessManager, QNetworkRequest, QNetworkReply,
                              QSslConfiguration, QSslSocket)

def main():
    # QCoreApplication 객체 생성
    app = QCoreApplication(sys.argv)

    # QNetworkAccessManager 객체 생성
    manager = QNetworkAccessManager()

    # SSL 지원 여부 확인
    print("SSL 지원:", QSslSocket.supportsSsl())
    print("SSL 빌드 버전:", QSslSocket.sslLibraryBuildVersionString())
    print("SSL 실행 버전:", QSslSocket.sslLibraryVersionString())

    # fetch의 then과 유사한 역할을 하는 콜백 함수
    def on_finished(reply: QNetworkReply):
        print("\n=== 네트워크 응답 정보 ===")
        print("응답 상태:", reply.attribute(QNetworkRequest.HttpStatusCodeAttribute))
        print("에러 코드:", reply.error())
        print("에러 메시지:", reply.errorString())
        
        # 헤더 정보 출력
        print("\n=== 응답 헤더 ===")
        headers = reply.rawHeaderList()
        for header in headers:
            # QByteArray를 str로 올바르게 변환
            header_str = str(header, 'utf-8')
            value_str = str(reply.rawHeader(header_str), 'utf-8')
            print(f"{header_str}: {value_str}")

        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            try:
                json_data = json.loads(str(bytes(data).decode('utf-8')))
                print("\n=== 응답 데이터 ===")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print("JSON 파싱 에러:", e)
                print("원본 데이터:", str(bytes(data).decode('utf-8')))
        else:
            print("\n=== SSL 에러 정보 ===")
            print("SSL 핸드셰이크 에러:", reply.sslErrors())

        reply.deleteLater()
        app.quit()

    # SSL 설정
    ssl_config = QSslConfiguration.defaultConfiguration()
    ssl_config.setPeerVerifyMode(QSslSocket.VerifyNone)  # 개발 테스트용

    # finished 시그널에 콜백 연결
    manager.finished.connect(on_finished)

    # fetch URL과 동일한 엔드포인트 사용
    url = QUrl("https://jsonplaceholder.typicode.com/todos/1")
    request = QNetworkRequest(url)
    request.setSslConfiguration(ssl_config)
    request.setHeader(QNetworkRequest.UserAgentHeader, "MyTestApp/1.0")

    print("\n=== 요청 시작 ===")
    print("요청 URL:", url.toString())
    # GET 요청 전송 (fetch와 동일)
    manager.get(request)

    # 이벤트 루프 실행
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
