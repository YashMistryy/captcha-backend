from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from game.models import Plan
from game.serializers import PlanSerializer
import logging
from django.utils import timezone

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
        selected_plan = Plan.objects.get(id=plan_id)
        print(selected_plan)
        # now enroll user
        CaptchaPlanRecord.objects.create(user=user,plan=selected_plan)
        user.current_balance += selected_plan.amount
        user.save()
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
    return Response({"is_having_plan":False,"is_plan_activated":False})

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
            user.current_balance += 2
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
            'last_name':user.first_name,
            'email':user.email,
            "mobile_number":user.mobile_number,
            'plan_name':ce.plan.name,
            'total_captcha_filled':ce.total_captchas_filled,
            'captcha_limit':ce.plan.captcha_limit,
            'current_balance':user.current_balance,
        }
        return Response(status=status.HTTP_200_OK,data=data)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={"msg":f"something went wrong at server {e}"})
    
    
def reset_daily_captcha_record():
    # make it 0 if last_filled_captcha was before today
    pass