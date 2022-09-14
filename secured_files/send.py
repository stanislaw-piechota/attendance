from main.commands import send_mails as sm
from main.models import Student as st, VerificationCode as vc


sm(st, vc)