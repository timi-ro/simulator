from django.views.decorators.csrf import csrf_exempt

from spyne.server.django import DjangoApplication
from spyne.model.primitive import Unicode, Integer, String
from spyne.model.complex import ComplexModel
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.application import Application
from spyne.decorator import rpc
from apps.core import status
from random import randint
import time


class UserCredential(ComplexModel):
    username = String
    password = String


class SendSmsReturn(ComplexModel):
    errorMsg = String
    status = Integer
    existsNumberCount = Integer
    orderId = Integer


class ReportItems(ComplexModel):
    initDate = Integer
    orderId = Integer
    successDelivered = Integer
    totalSent = Integer


class GetReportReturn(ComplexModel):
    errorMsg = String
    status = Integer
    reportItem = ReportItems


class SDPSimulator(ServiceBase):
    @rpc(UserCredential, Unicode, Unicode.customize(max_occurs=50), Unicode, Integer,
         _returns=SendSmsReturn.customize(sub_name='return'))
    def sendSms(ctx, userCredential, srcAddress, regionIds, msgBody, maxSendCount):
        order_id = randint(1000000, 99999999999999)
        exist_number_count = randint(1, maxSendCount)

        if userCredential.username is None:
            return SendSmsReturn(errorMsg='Username is empty.', status=status.SEND_USERNAME_NOT_SPECIFIED)
        elif userCredential.password is None:
            return SendSmsReturn(errorMsg='Password is empty.', status=status.SEND_PASSWORD_NOT_SPECIFIED)
        elif srcAddress is None:
            return SendSmsReturn(errorMsg='source number is empty.', status=status.SEND_SRC_NOT_SPECIFIED)
        elif regionIds is None:
            return SendSmsReturn(errorMsg='Region ID not found: 0', status=status.SEND_RECEIVER_NOT_FOUND)
        elif msgBody is None:
            return SendSmsReturn(errorMsg='message body is empty.', status=status.SEND_MSG_BODY_NOT_SPECIFIED)
        elif msgBody is None:
            return SendSmsReturn(errorMsg='message body is empty.', status=status.SEND_MSG_BODY_NOT_SPECIFIED)
        elif maxSendCount is None:
            return SendSmsReturn(errorMsg='maxSendCount should be greater than 0',
                                 status=status.SEND_MAX_SEND_COUNT_INVALID)
        elif maxSendCount > 2000:
            return SendSmsReturn(errorMsg='maxSendCount should be lower than 2000',
                                 status=status.SEND_MAX_SEND_COUNT_EXCEEDED)
        else:
            return SendSmsReturn(status=0, existsNumberCount=exist_number_count, orderId=order_id)

    @rpc(UserCredential, Integer, _returns=GetReportReturn.customize(sub_name='return'))
    def getReportByOrderId(ctx, userCredential, orderIds):
        total_sent = randint(1, 2000)
        success_delivered = randint(10, total_sent)
        init_date = int(1000 * (time.time() - randint(1, 7200)))

        if userCredential.username is None:
            return GetReportReturn(errorMsg='Username is empty.', status=status.SEND_USERNAME_NOT_SPECIFIED)
        elif userCredential.password is None:
            return GetReportReturn(errorMsg='Password is empty.', status=status.SEND_PASSWORD_NOT_SPECIFIED)
        else:
            report_items = ReportItems(initDate=init_date, orderId=orderIds, successDelivered=success_delivered,
                                       totalSent=total_sent)
            result = GetReportReturn(status=0, reportItem=report_items)
            return result


app = Application([SDPSimulator],
                  'localhost',
                  in_protocol=Soap11(validator='lxml'),
                  out_protocol=Soap11(),
                  )

lbs_sdp_service = csrf_exempt(DjangoApplication(app))
