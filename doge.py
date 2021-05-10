import time
import pyupbit
import datetime
import requests

access = ""
secret = ""
myToken = ""

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
   # post_message(myToken,"#stock", "target_price : " +  str(target_price))
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    #post_message(myToken,"#stock", "start_time : " +  str(start_time))
    return start_time

def get_ma15(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    #post_message(myToken,"#stock", "15 day mov avg : " +  str(ma15))
    return ma15

def get_balance(coin):
    """잔고 조회 50%만 조회"""
    balances = upbit.get_balances()
    #post_message(myToken,"#stock", "now my coin  : " +  str(balances))
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                # print("balance" + str(float(b['balance'])))
                # print("balance/50" + str(float(b['balance'])/50))
                return float(b['balance'])/50
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
   # post_message(myToken,"#stock", "now pay : " +  str(pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]))
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade doge start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#stock", "autotrade doge start")

while True:
    try:
        get_balance("KRW")
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-DOGE")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            # 변동성 돌파 전략으로 매수 목표가 조회
            target_price = get_target_price("KRW-DOGE", 0.5)
            # 15일 이동 평균선 조회
            ma15 = get_ma15("KRW-DOGE")
            # 현재가 조회
            current_price = get_current_price("KRW-DOGE")
            if target_price < current_price and ma15 < current_price:
                # 잔고 조회
                krw = get_balance("KRW")
                if krw > 5000:
                    # 사장가 매수
                    buy_result = upbit.buy_market_order("KRW-DOGE", krw*0.9995)
                    post_message(myToken,"#stock", "order start")
                    post_message(myToken,"#stock", "doge buy  krw > 5000 : " +str(buy_result))
                    post_message(myToken,"#stock", "start_time : " +str(start_time))
                    post_message(myToken,"#stock", "noew krw  : " +str(krw))
                    post_message(myToken,"#stock", "target_price  : " +str(target_price))
                    post_message(myToken,"#stock", "15day mov avg  : " +str(ma15))
                    post_message(myToken,"#stock", "order end")
        else:
            doge = get_balance("doge")
            if doge > 0.00008:
                # 시장가 매도
                sell_result = upbit.sell_market_order("KRW-DOGE", doge*0.9995)
                post_message(myToken,"#stock", "doge buy : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#stock", "doge error : " + str(e))
        time.sleep(1)