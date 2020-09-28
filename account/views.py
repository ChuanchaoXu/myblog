import random
from django.contrib.auth.models import User
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from account.forms import *
from account.models import UserInfo


def sendEmail(receive, username, action, code):
    """
    :param str receive: 收件人
    :param str username: 收件人用户名
    :param str action: 操作内容
    :param str code: 验证码
    :return: 1 发送成功
    """
    content = """
    <body style="background-color: #ebedf0;margin: 0;padding: 0">
        <div id="content" style="width: 75%;margin: 10% auto;background-color: white;border-radius: 10px;box-shadow: 0 0 15px 1px rgba(0, 0, 0, 0.4);">
            <div style="text-align: center;background-color: #ecf0f1;height: 80px">
                <h2 style="margin: 0 auto;line-height: 80px;">【崔亮的博客】验证码</h2>
            </div>
            <div style="padding: 0 20px;">
                <p style="font-weight: bold">尊敬的""" + username + """：您好！</p>
                <p style="text-indent:2em;font-weight: bold">您正在进行
                    <span style="color: #e74c3c">""" + action + """</span>操作，请在验证码输入框输入：
                    <span style="color: #e74c3c;font-weight: bold;font-size: 40px">""" + code + """</span>，以完成操作，验证码有效期为3分钟。
                </p>
                <br>
                <p style="color: #bdc3c7;text-indent:2em">注意：此操作可能会对您的账号进行""" + action + """操作。
                    如非本人操作，请及时登录并修改密码以保证账户安全，请勿泄露此验证码！</p>
            </div>
            <div style="background-color: #ecf0f1;padding: 20px;">
                <p style="color: #bdc3c7;text-indent:2em;margin: 0 auto;line-height: 30px">您会收到这封邮件，是由于在
                    <a href="https://www.cuiliangblog.cn" style="text-decoration: none">崔亮的博客</a>
                    进行了新用户注册或修改密码、重置密码操作。如果您并没有访问过
                    <a href="https://www.cuiliangblog.cn" style="text-decoration: none">崔亮的博客</a>
                    ，或没有进行上述操作， 请忽略这封邮件！
                </p>
            </div>
        </div>
        <script>
            var width = document.body.clientWidth;
            if (width < 500) {
                document.querySelector("#content").style.width="95%"
            }
        </script>
    </body>
    """
    subject = "[崔亮的博客] Email 验证码"
    from_email = "崔亮的博客<cuiliangblog@qq.com>"
    msg = EmailMultiAlternatives(subject, content, from_email, [receive])
    msg.content_subtype = "html"
    return msg.send()


# 设置邮箱、用户名都可以登录
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            print(e)
            return None


# 登录注册页
def loginRegister(request):
    if request.method == "POST":
        type = request.POST.get('type')
        if type == "登录":
            login_form = LoginForm(request.POST)
            # 创建一个对象，获得post方法提交的数据
            if login_form.is_valid():
                # 验证传入的数据是否合法
                login_data = login_form.cleaned_data
                # 引入字典数据类型，存储用户名和密码
                user = authenticate(username=login_data['user'], password=login_data['password'])
                # 验证账号密码是否正确，正确返回user对象，错误返回null
                if user:
                    # 调用django默认的login方法，实现用户登录
                    login(request, user)
                    # 登录后跳转的页面
                    next_url = request.GET.get("next")
                    if next_url:
                        print(next_url)
                        return HttpResponseRedirect(next_url)
                    else:
                        return HttpResponseRedirect('/')
                else:
                    message = '用户名或密码错误！'
                    hashkey = CaptchaStore.generate_key()
                    image_url = captcha_image_url(hashkey)
                    login_form = LoginForm()
                    register_form = RegisterForm()
                    print(message)
                    return render(request, "account/loginRegister.html", locals())
            else:
                message = '验证码错误！'
                hashkey = CaptchaStore.generate_key()
                image_url = captcha_image_url(hashkey)
                login_form = LoginForm()
                register_form = RegisterForm()
                print(message)
                return render(request, "account/loginRegister.html", locals())

        if type == "注册":
            register_form = RegisterForm(request.POST)
            # 创建一个对象，获得post方法提交的数据
            if register_form.is_valid():
                register_data = register_form.cleaned_data
                # 校验邮件验证码
                try:
                    session_code = request.session['email_code']
                except KeyError:
                    data = {
                        "code": 0,
                        "msg": "邮件验证码已过期！"
                    }
                    return JsonResponse(data)
                if register_data['email_code'] != session_code:
                    data = {
                        "code": 0,
                        "msg": "邮件验证码错误！"
                    }
                    return JsonResponse(data)
                # 校验通过，创建用户
                username = register_data['username']
                password = register_data['password1']
                email = register_data['email']
                new_user = User.objects.create()
                new_user.username = username
                new_user.set_password(password)
                new_user.email = email
                new_user.save()
                # 创建用户信息表记录
                UserInfo.objects.create(user_id=new_user.id)
                # 创建完用户自动登录
                user = authenticate(username=username, password=password)
                # 调用django默认的login方法，实现用户登录
                login(request, user)
                data = {
                    "code": 1,
                    "msg": "注册成功，自动跳转至首页并登陆！"
                }
                return JsonResponse(data)
            else:
                ErrorDict = register_form.errors
                print(ErrorDict)
                data = {
                    "code": 0,
                    "msg": "请求数据异常！"
                }
                return JsonResponse(data)

    else:
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        login_form = LoginForm()
        register_form = RegisterForm()
        return render(request, 'account/loginRegister.html', locals())


# 忘记密码
def forgetPassword(request):
    if request.method == "POST":
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            forget_data = forget_form.cleaned_data
            email = forget_data['email']
            password = forget_data['password1']
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            data = {
                "code": 1,
                "msg": "密码重置成功！"
            }
            return JsonResponse(data)
        else:
            ErrorDict = forget_form.errors
            print(ErrorDict)
            data = {
                "code": 0,
                "msg": "请求数据异常！"
            }
            return JsonResponse(data)

    else:
        forget_form = ForgetForm()
        return render(request, 'account/forgetPassword.html', locals())


@login_required()
# 判断用户是否登录，django自带的装饰器函数
# 个人中心
def personalCenter(request):
    userinfo = UserInfo.objects.get(user_id=request.user.id)
    user = User.objects.get(username=request.user)
    return render(request, 'account/personalCenter.html', locals())


# 修改密码
@login_required()
def changePassword(request):
    if request.method == "POST":
        change_password_form = ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            change_password_data = change_password_form.cleaned_data
            old_password = change_password_data['password_old']
            new_password = change_password_data['password1']
            user = authenticate(username=request.user.username, password=old_password)
            # 验证账号密码是否正确，正确返回user对象，错误返回null
            if user:
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect('/account/logout/')
            else:
                message = "原始密码错误！"
        else:
            message = "表单数据异常！"
        change_password_form = ChangePasswordForm()
        return render(request, 'account/changePassword.html', locals())
    else:
        change_password_form = ChangePasswordForm()
        return render(request, 'account/changePassword.html', locals())


# 修改邮箱
@login_required()
def changeEmail(request):
    if request.method == "POST":
        change_email_form = ChangeEmailForm(request.POST)
        if change_email_form.is_valid():
            change_email_data = change_email_form.cleaned_data
            password = change_email_data['password']
            email = change_email_data['email']
            email_code = change_email_data['email_code']
            user = authenticate(username=request.user.username, password=password)
            # 验证账号密码是否正确，正确返回user对象，错误返回null
            if user:
                # 校验邮件验证码
                try:
                    session_code = request.session['email_code']
                except KeyError:
                    message = '验证码过期！'

                if email_code != request.session['email_code']:
                    message = '验证码错误！'
                else:
                    # 验证通过，修改邮箱号
                    user = request.user
                    user.email = email
                    user.save()
                    return HttpResponseRedirect('/account/personalCenter/')
                change_email_form = ChangeEmailForm()
                return render(request, 'account/changeEmail.html', locals())
            else:
                message = "密码错误！"
            change_email_form = ChangeEmailForm()
            return render(request, 'account/changeEmail.html', locals())
        else:
            message = change_email_form.errors
        change_email_form = ChangeEmailForm()
        return render(request, 'account/changeEmail.html', locals())
    else:
        change_email_form = ChangeEmailForm()
        return render(request, 'account/changeEmail.html', locals())


# 修改信息
@login_required()
def changeInformation(request):
    userinfo = UserInfo.objects.get(user_id=request.user.id)
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST)
        userinfo_form = UserInfoForm(request.POST)
        if userinfo_form.is_valid():
            userinfo_data = userinfo_form.cleaned_data
            userinfo.sex = userinfo_data['sex']
            userinfo.phone = userinfo_data['phone']
            userinfo.web = userinfo_data['web']
            userinfo.aboutme = userinfo_data['aboutme']
            request.user.save()
            userinfo.save()
            return HttpResponseRedirect('/account/personalCenter/')
        else:
            return render(request, 'account/changeInformation.html', locals())
    else:
        username = user.username
        email = user.email
        user_form = UserForm({'username': username, 'email': email})
        sex = userinfo.sex
        phone = userinfo.phone
        web = userinfo.web
        aboutme = userinfo.aboutme
        userinfo_form = UserInfoForm({'sex': sex, 'phone': phone, 'web': web, 'aboutme': aboutme})
        return render(request, 'account/changeInformation.html', locals())


# 浏览记录
def historyBrowse(request):
    browseList = []
    for i in range(1, 11):
        browseList.append(i)
    return render(request, 'account/historyBrowse.html', locals())


# 评论记录
def historyComment(request):
    commentList = []
    for i in range(1, 11):
        commentList.append(i)
    return render(request, 'account/historyComment.html', locals())


# 收藏记录
def historyCollection(request):
    collectionList = []
    for i in range(1, 11):
        collectionList.append(i)
    return render(request, 'account/historyCollection.html', locals())


# 留言记录
def historyLeave(request):
    scoreList = []
    for i in range(1, 11):
        scoreList.append(i)
    return render(request, 'account/historyLeave.html', locals())


# ajax用户注册验证
def registerCheck(request):
    username = request.GET.get('username')
    if username is not None:
        if User.objects.filter(username=username).exists():
            data = {
                "code": 0,
                "msg": "用户名已存在"
            }
        else:
            data = {
                "code": 1,
                "msg": "用户名可以使用"
            }
        return JsonResponse(data)
    email = request.GET.get('email')
    if email is not None:
        if User.objects.filter(email=email).exists():
            data = {
                "code": 0,
                "msg": "邮箱已注册"
            }
        else:
            data = {
                "code": 1,
                "msg": "邮箱可以使用"
            }
        return JsonResponse(data)


# ajax获取邮件验证码
def emailCode(request):
    if request.method == "GET":
        email = request.GET["email"]
        action = request.GET["action"]
        if action == "注册新用户":
            username = "新用户"
        elif action == "重置密码":
            username = str(User.objects.get(email=email))
        elif action == "更换邮箱":
            username = str(request.GET["username"])
        email_code = ""
        for i in range(6):
            email_code = email_code + str(random.randint(0, 9))
        request.session['email_code'] = email_code
        # 过期时间 单位s
        request.session.set_expiry(180)
        action = request.GET["action"]
        if sendEmail(email, username, action, email_code):
            data = {
                "code": 1,
                "msg": "验证码已发送"
            }
        else:
            data = {
                "code": 0,
                "msg": "验证码发送失败"
            }
    return JsonResponse(data)


# ajax 检查邮件验证码
def checkEmailCode(request):
    if request.method == "POST":
        # 校验邮件验证码
        request_code = request.POST.get('email_code')
        try:
            session_code = request.session['email_code']
        except KeyError:
            data = {
                "code": 0,
                "msg": "邮件验证码已过期！"
            }
            return JsonResponse(data)
        if request_code != session_code:
            data = {
                "code": 0,
                "msg": "邮件验证码错误！"
            }
            return JsonResponse(data)
        # 校验通过
        else:
            data = {
                "code": 1,
                "msg": "邮件验证码校验通过！"
            }
            return JsonResponse(data)


# ajax头像上传
def photoUpload(request):
    if request.method == "POST":
        dir = 'photo/'
        file = request.FILES.get('file')
        filename = "%s.%s" % (timezone.now().strftime('%Y_%m_%d_%H_%M_%S_%f'), file.name.split('.')[-1])
        filepath = 'media/' + dir + filename
        # 图片资源写入服务器
        code = upload(file, filepath)
        if (code == 1):
            # 图片路径写入数据库
            url = dir + filename
            print(url)
            userinfo = UserInfo.objects.get(user_id=request.user.id)
            print(userinfo.photo)
            userinfo.photo = url
            userinfo.save()
            data = {
                "msg": "上传成功",
                "src": filepath,
                "code": "1",
            }
            return JsonResponse(data)
        else:
            data = {
                "msg": "上传失败",
                "code": "0",
            }
        return JsonResponse(data)


# 图片保存
def upload(file, filepath):
    try:
        with open(filepath, 'wb+') as f:
            for chrunk in file.chunks():
                f.write(chrunk)
        f.close()
        return 1
    except:
        return 0
