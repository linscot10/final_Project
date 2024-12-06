from django.shortcuts import render,redirect
from my_app.models import Product,Orders,OrderUpdate,Contact
from math import ceil
from .key import MpesaPassword,MpesaAccessToken,MpesaCredentials
import base64
import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt


import json

# Create your views here.


def home(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}
    return render(request,'index.html',params)



def handlerequest(request):
    return render(request,'handlerequest.html')
    
def purchase(request):
 
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}
    return render(request,'purchase.html',params)


def contactus(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        messages.success(request,"Contact Form is Submitted")
  
    return render(request, 'contact.html')


def get_mpesa_token():
    consumer_key = MpesaCredentials.consumer_key
    consumer_secret = MpesaCredentials.consumer_secret
    api_url = MpesaCredentials.api_url
    headers = {"Authorization": f"Basic {base64.b64encode(f'{consumer_key}:{consumer_secret}'.encode()).decode()}"}
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        return None 



def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    
    if request.method == "POST":
      
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        location = request.POST.get('location', '')
        zip_code = request.POST.get('zip_code', '')
       
        
        
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,location=location,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True
        id = Order.order_id
        oid=str(id)
        oid=str(id)
        
        

      
        access_token = get_mpesa_token()
       
        # api_url='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        # headers={"Authorization":"Bearer %s" % access_token} 
        payment_data = {
            'ORDER_ID': oid,
            "Password": MpesaPassword.decode_password,    
            "Timestamp":MpesaPassword.lipa_time,    
            "TransactionType": "CustomerPayBillOnline",    
            "BusinessShortcode":MpesaPassword.bussiness_short_code,
            "Amount": amount,
            "PartyA": phone, 
            "PartyB": MpesaPassword.bussiness_short_code,  
            "PhoneNumber": phone, 
            "CallBackURL": "http://localhost:8000/handlerequest/",  
            "AccountReference": f"Order-{Order.order_id}",
            "TransactionDesc": "Payment for order"
        }
        
        

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response =requests.post(api_url,json=payment_data,headers=headers)
       
        response_data = response.json()

        if response.status_code == 200 and 'ResponseCode' in response_data and response_data['ResponseCode'] == '0':
           
            return redirect(response_data['CheckoutRequestID'])
        
       
        messages.error(request, "Payment initiation failed. Please try again.")
        return redirect('/handlerequest/')

    return render(request, 'checkout.html')
   
      


@csrf_exempt
def handlerequest(request):
   
        
   
        response_dict = request.POST
        print(response_dict)
        
        status = response_dict.get('Status', '')
        order_id = response_dict.get('OrderId', '')
        amount = response_dict.get('Amount', '')
        
        if status == '1':  
            try:
                order = Orders.objects.get(order_id=order_id)
                order.payment_status = "PAID"
                order.amount_paid = amount
                order.save()
                messages.success(request, "Payment Successful")
            except Orders.DoesNotExist:
                messages.error(request, f"Order with ID {order_id} not found.")
                return redirect('/checkout/')
        
            return render(request, 'paymentstatus.html', {'response': response_dict, 'status': 'success'})
        else:
        
            messages.error(request, "Payment failed.")
            return render(request, 'paymentstatus.html', {'response': response_dict, 'status': 'failure'})\
                
   
        
    
    


def tracker(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'tracker.html')



