logger.debug('Sending notification to app.')
    news = News.objects.get(pk=pk)
    if not news:
        logger.debug('News not available.')
        return

    try:
        url = 'https://fcm.googleapis.com/fcm/send'
        headers = {
            'Authorization': 'key=',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        json = {
            "notification": {
                "title": news.title,
                "body": news.description(),
                "sound": "default"
            },
            "priority": "high", 
            "data": {
                "click_action": "FLUTTER_NOTIFICATION_CLICK", 
                "id": news.id,
                "title": news.title,
                "status": "done"
            },
            "to": "/topics/app"
        }
    
        r = requests.post(url, json=json, headers=headers)
        if(r.status_code != 200):
            # Failed pushing notification
            logger.debug('Failed to send notification to app.')
            news.notification = False
            news.save()
        logger.debug('Notification send to app successfully.')
    except Exception as e:
        # Failed pushing notification
        logger.debug('Failed to send request for app.')
        logger.debug(str(type(e)) + ' : ' + str(e))
        news.notification = False
        news.save()
