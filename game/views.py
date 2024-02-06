from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from game.models import Plan,PaymentTransaction,WithdrawTransaction
from game.serializers import PlanSerializer
import logging
from django.utils import timezone
from users.models import User
import traceback

# logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s [%(levelname)s] - %(message)s')

from game.models import Plan,CaptchaPlanRecord

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def greet(request):
    user = request.user
    data = {"name":user.first_name+" "+user.last_name,"member_id":user.member_id,"phone_number":user.mobile_number}
    return Response(data=data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plan_details(request):
    # print("********************************* get plant details",request.GET)
    plan_id = int(request.query_params.get('planId'))
    plan = Plan.objects.get(id=plan_id)
    serializer = PlanSerializer(plan)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_plan(request):
    data = request.data
    user = request.user
    print(data)
    print(user)
    # now with the available details like user ,plan_id and transaction details we can enroll user into a plan , but not activate it just yet
    try:
        plan_id = int(data.get('plan_id'))
        refferal_id = (data.get('refferal_id'))
        
        selected_plan = Plan.objects.get(id=plan_id)
        print(selected_plan)
        # now enroll user
        if (user.current_balance < selected_plan.amount):
            return Response(status=status.HTTP_204_NO_CONTENT,data={"msg":"low_balance"})
        CaptchaPlanRecord.objects.create(user=user,plan=selected_plan,is_plan_active=True)
        user.current_balance -= selected_plan.amount
        user.save()
        try:
            user_objs = User.objects.filter(referral_id=refferal_id)
            if user_objs: # only if referal id is correct we are going to increase both user's balance
                user1 = user_objs[0]
                user1.current_balance += selected_plan.referral_amount
                user1.save()
                user.current_balance += 500 #selected_plan.referral_amount
                user.save()
        except Exception as e:
            print("************************* ecxeption {e}".format(e))
            pass
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}\n{traceback.format_exc()}")       
        return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":"Plan was Not Selected  :( Maybe user is already enrolled in a Plan"})
    return Response({"msg":"plan selected"})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_if_enrolled(request):
    # if user have a plan then send the details else Empty response
    user= request.user
    objs = CaptchaPlanRecord.objects.filter(user=user)
    if objs:
        ce = objs[0]
        today = timezone.now().date()
        if ce.last_captcha_fill_date != today:
            # If the last captcha fill date is not today, reset the count
            ce.captchas_filled_today = 0
            ce.save()
        return Response(
            {"is_having_plan":True,
             "is_plan_activated":ce.is_plan_active,
             "userData":{
                 "name":user.first_name+" "+user.last_name,
                 "member_id":user.member_id,
                 "phone_number":user.mobile_number,
                 "current_balance":user.current_balance},
             "planData":{
                 "captchas_filled":ce.captchas_filled_today,
                 "name":ce.plan.name,
                 "captcha_limit":ce.plan.captcha_limit}})
    return Response({"is_having_plan":False,"is_plan_activated":False,
                      "userData":{
                 "name":user.first_name+" "+user.last_name,
                 "member_id":user.member_id,
                 "phone_number":user.mobile_number,
                 "current_balance":user.current_balance},
             "planData":{
                 "captchas_filled":0,
                 "name":"",
                 "captcha_limit":0}})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_captcha(request):
    # user should be enrolled in a Plan then he can fill a captcha and plan must be active
    user = request.user
    pe = CaptchaPlanRecord.objects.filter(user=user)
    is_submission_ok = request.data.get("is_submission_ok",None)
    try:
        if not is_submission_ok:
            user.current_balance -= 1
            user.save()
            cr = pe[0]
            cr.fill_captcha()
            return Response(status=status.HTTP_206_PARTIAL_CONTENT,data={"msg":"wrong data sent hence deducting a coin"})
        if pe:
            # call the model class method fill_captcha to increment the value of captcha filled by user
            cr = pe[0]
            cr.fill_captcha()
            # also user should get his points or money increased!
            user.current_balance += 1
            user.save()
            return Response(status=status.HTTP_201_CREATED,data={"msg":"Captcha record filled!"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":"something wen wrong , maybe applied value was not correct!"})
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}\n{traceback.format_exc()}")   
        return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":"something went wrong at server"})
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    #get each detail about user and his plan(if any)
    user = request.user
    try:
        ce = CaptchaPlanRecord.objects.get(user=user)
        today = timezone.now().date()
        if ce.last_captcha_fill_date != today:
            # If the last captcha fill date is not today, reset the count
            ce.captchas_filled_today = 0
            ce.save()
        data = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'current_balance':user.current_balance,
            "mobile_number":user.mobile_number,
            'plan_name':ce.plan.name,
            'total_captcha_filled':ce.total_captchas_filled,
            'refferal_code':user.referral_id,
            'times_reffered':user.times_reffered,
            
            'captcha_limit':ce.plan.captcha_limit,
            'payment_history':PaymentTransaction.objects.filter(user=user).values(),
            'withdraw_history':WithdrawTransaction.objects.filter(user=user).values(),
        }
        return Response(status=status.HTTP_200_OK,data=data)
    except CaptchaPlanRecord.DoesNotExist:
        data = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'current_balance':user.current_balance,
            "mobile_number":user.mobile_number,
            'plan_name':"",
            'total_captcha_filled':0,
            'captcha_limit':0,
            'refferal_code':user.referral_id,
            'times_reffered':user.times_reffered,
            'payment_history':PaymentTransaction.objects.filter(user=user).values(),
            'withdraw_history':WithdrawTransaction.objects.filter(user=user).values(),
        }
        return Response(status=status.HTTP_200_OK,data=data)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":f"something went wrong at server {e}"})
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_amount(request):
    # just add an object to model here with status pending so that user can see it in Wallet section
    user = request.user
    try:
        amount = request.data.get("amount",None)
        upi_id = request.data.get("upi_id",None)
        bank_id = request.data.get("bank_id",None)
        if(amount and upi_id and bank_id):
            WithdrawTransaction.objects.create(user=user,status="Pending",amount=amount,upi_id=upi_id,bank_id=bank_id)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":"wrong data were present in request"})
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_206_PARTIAL_CONTENT)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_amount(request):
    # just add an object to model here with status pending so that user can see it in Wallet section
    user = request.user
    try:
        amount = request.data.get("amount",None)
        # upi_id = request.data.get("upi_id",None)
        # refferal_id = request.data.get("refferal_id",None) # wiht this increase the referal amount by 500 for e botht the users
        # user_objs = User.objects.filter(referral_id=refferal_id)
        # if user_objs: # only if referal id is correct we are going to increase both user's balance
        #     user1 = user_objs[0]
        #     user1.current_balance += 500
        #     user1.save()
        #     amount = int(amount)+500  
        transactionId = request.data.get("transactionId",None)
        if(amount and transactionId):
            PaymentTransaction.objects.create(user=user,status="Pending",amount=amount,transactionId=transactionId)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":"wrong data were present in request"})
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_412_PRECONDITION_FAILED)
    
def reset_daily_captcha_record():
    # make it 0 if last_filled_captcha was before today
    pass