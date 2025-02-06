import serial
import time

def main():
    # 시리얼 포트 설정
    port = 'COM9'
    baud_rate = 112500
    
    try:
        # 시리얼 포트 연결
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"포트 {port}에 연결되었습니다.")
        
        while True:
            # 수신 데이터가 있는 경우
            if ser.in_waiting:
                # 데이터 읽기
                data = ser.read(ser.in_waiting)
                # 16진수로 변환하여 출력
                print(f"수신 데이터: {data.hex()}")
            
            # CPU 부하 감소를 위한 대기
            time.sleep(0.01)
            
    except serial.SerialException as e:
        print(f"시리얼 포트 연결 오류: {e}")
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("시리얼 포트 연결이 해제되었습니다.")

if __name__ == "__main__":
    main()
