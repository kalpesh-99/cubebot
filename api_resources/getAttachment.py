
def getAttachment(attachment):
    attachmentList = attachment
    for item in attachmentList:
        for key in item:
            if key == 'type':
                attachmentType = item['type']
                if attachmentType == 'fallback':
                    print("got fallback attachment type from getAttachment.py")
                    attachmentTitle = item['title']
                    attachmentText = "Got it, I'll file '%s' for safe keeping!" %attachmentTitle
                elif attachmentType == 'template':
                    print("got template attachment type")
                    attachmentTitle = item['title']
                    attachmentText = "Got it, I'll file '%s' for safe keeping!" %attachmentTitle

                else:
                    payload_url = item['payload']['url']
                    attachmentText = "Ok, I'll save this attachment under: " +attachmentType
                    print(payload_url) ## need to use this payload_url to get imgURL
                print(attachmentType)
        # receivedAttachment(attachmentText, sender_id)
        return attachmentText
