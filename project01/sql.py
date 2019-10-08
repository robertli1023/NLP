 sql = """
#        SELECT * FROM user WHERE username=%s
#    """
#    res = Do_sql.readdb(sql, (username, ))
#    if not res:
        ver_code = Do_common.create_ver_code()
        apply_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        sql = """
            SELECT * FROM user_sign WHERE username=%s
        """
        res = Do_sql.readdb(sql, (username,))
        if len(res) > 0:
            res = res[0]
            apply_s = int(time.mktime(time.strptime(str(res['apply_time']), "%Y-%m-%d %H:%M:%S")))
            active_s = int(time.mktime(time.strptime(apply_time, "%Y-%m-%d %H:%M:%S")))

            if res['apply_res'] == 0 and active_s - apply_s < 3600:
                return {"get_ver_code_state": "操作过于频繁，上一个验证码仍有效。"}

        msg = "注册验证码，请查收".encode('utf-8')
        msg_text = "\n你有两次尝试机会，两次输错验证码，则验证码失效。"
        variable = Do_common.mail_do(username, ver_code, msg, msg_text)
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(variable['mail_host'], 25)  # 25 为 SMTP 端口号
            smtpObj.login(variable['mail_user'], variable['mail_pass'])
            smtpObj.sendmail(variable['mail_user'], variable['receivers'], variable['message'].as_string())

            sql = """
                INSERT INTO user_sign (username, ver_code, apply_time) VALUES (%s, %s, %s)
            """
            res = Do_sql.writedb(sql, (username, ver_code, apply_time))
            if res:
                return {"get_ver_code_state": "验证码已发送，可能被当成垃圾邮件。"}
            else:
                return {"get_ver_code_state": "未知错误，邮件发送错误，请重试。"}
        except smtplib.SMTPException:
            return {"get_ver_code_state": "未知错误，邮件发送错误，请重试。"}
    else:
        return {"get_ver_code_state": "邮箱已被注册，请更换邮箱。"}