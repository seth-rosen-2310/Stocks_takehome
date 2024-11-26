from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import openai
from . import logic

#Basic function to handle user request
def index(request):
  if request.method == 'POST':

    query = request.POST.get('query')
    result = logic.llm_call(query)
    resultJson = JsonResponse(result)
    return resultJson
  return render(request, 'th_app/index.html')