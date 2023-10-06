from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
import requests
from .models import LineToken, Message
from .forms import MessageForm
from django.views.decorators.csrf import csrf_exempt

# 開啟 LINE Notify 畫面
def open_line_oauth(request):
    # LINE Notify 管理登錄服務中可以找到對應服務的 CLIENTID
    YOUR_CLIENT_ID = '2OGLl9To1DW8opKVieTxgP'
    # LINE Notify 管理登錄服務中可以找到對應服務的 Callback URL，Callback URL需要自己設定
    YOUR_REDIRECT_URI = 'https://a491-42-77-199-157.ngrok-free.app/callback/'
    # 用來驗證的字樣,參數寫死
    YOUR_STATE_VALUE = 'random_state_string'

    # LINE Notify 官方 API 文件：https://notify-bot.line.me/doc/en/
    # 獲取 LINE Notify 認證 
    url = f"https://notify-bot.line.me/oauth/authorize?response_type=code&client_id={YOUR_CLIENT_ID}&redirect_uri={YOUR_REDIRECT_URI}&scope=notify&state={YOUR_STATE_VALUE}"
    
    return HttpResponseRedirect(url)

# 取得 CALLBACK 的驗證字串，獲取 LINE Notify 發送訊息的 TOKEN
def callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Authorization code not found.", status=400)
    
    extracted_code = code
    # 透過 API 去取得 TOKEN
    token_response = taketoken(extracted_code)

    if not token_response.get('success'):
        return HttpResponse(token_response.get('message', "Error"), status=500)

    print("Redirecting to close_page")
    # 因為取完 TOKEN 的頁面是沒有作用的，考慮到使用者體驗要設計一頁面跳轉
    return HttpResponseRedirect('/close/')

# 透過 API 去取得 TOKEN
def taketoken(extracted_code):
    token_url = "https://notify-bot.line.me/oauth/token"
    headers = {
        # 參數寫死
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        # 參數寫死
        "grant_type": "authorization_code",
        "code": extracted_code,
        "redirect_uri": "https://a491-42-77-199-157.ngrok-free.app/callback/",
        "client_id": "2OGLl9To1DW8opKVieTxgP",
        "client_secret": "ksYER8YbFt27gEACDFEHXP2Gb7Uk9CfgtsYoh3VgQ8D" 
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        return {"success": False, "message": "Error fetching access token."}

    # 將 Token寫入資料庫
    access_token = response.json().get("access_token")
    LineToken.objects.create(access_token=access_token)
    return {"success": True, "token": access_token}

def close_page(request):
    return render(request, 'close_page.html')

# 透過 API 去寄送 LINE 警報通知
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message_text = form.cleaned_data.get('text')
            
            # 從資料庫中取得最新的access token
            line_token = LineToken.objects.last()
            if not line_token:
                return HttpResponse("No access token found.", status=400)
            
            # 發送 LINE 通知
            headers = {
                "Authorization": f"Bearer {line_token.access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "message": message_text
                
            }
            response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
            
            if response.status_code == 200:
                return redirect('message_sent')
            else:
                return HttpResponse("Failed to send LINE Notify message.", status=500)
    else:
        form = MessageForm()
    
    return render(request, 'send_message.html', {'form': form})

def message_sent(request):
    return render(request, 'message_sent.html')