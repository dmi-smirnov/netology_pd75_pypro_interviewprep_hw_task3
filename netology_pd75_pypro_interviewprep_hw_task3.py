import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import imaplib


class Email:
  smtp_srv_addr: str
  smtp_srv_port: int

  imap_srv_addr: str
  imap_srv_port: int
  
  user_name: str
  user_pwd: str

  def __init__(self, smtp_srv_addr: str, smtp_srv_port: int = 587,
               imap_srv_addr: str, imap_srv_port: int = 993,
               user_name: str, user_pwd: str) -> None:
    self.smtp_srv_addr = smtp_srv_addr
    self.smtp_srv_port = smtp_srv_port
    self.imap_srv_addr = imap_srv_addr
    self.imap_srv_port = imap_srv_port
    self.user_name = user_name
    self.user_pwd = user_pwd

  def send(self, from_addr: str = '', to_addrs: list[str], subject: str = '',
           msg_text: str = '') -> None:
    message = MIMEMultipart()

    if from_addr:
      message['From'] = from_addr
    else:
      message['From'] = self.user_name
    message['To'] = ', '.join(to_addrs)
    message['Subject'] = subject

    message.attach(MIMEText(msg_text))

    smtp = smtplib.SMTP(self.smtp_srv_addr, self.smtp_srv_port)
    # Identify ourselves to smtp client
    smtp.ehlo()
    # Secure our email with tls encryption
    smtp.starttls()
    # Re-identify ourselves as an encrypted connection
    smtp.ehlo()

    smtp.login(self.user_name, self.user_pwd)
    smtp.sendmail(from_addr, to_addrs, message.as_string())

    smtp.quit()

  def receive(self, mailbox: str = 'inbox',
              subject_filter: str | None = None):
    imap = imaplib.IMAP4_SSL(self.imap_srv_addr, self.imap_srv_port)

    imap.login(self.user_name, self.user_pwd)
    imap.list()
    imap.select(mailbox)

    criterion =\
      '(HEADER Subject "%s")' % subject_filter if subject_filter else 'ALL'
    
    __, data = imap.uid('search', criterion)

    if not data[0]:
      raise Exception('There are no letters with current header')

    latest_message_uid = data[0].split()[-1]
    __, data = imap.uid('fetch', latest_message_uid, '(RFC822)')
    raw_message = data[0][1]

    imap.logout()

    return email.message_from_string(raw_message)

def demo():
  email = Email(
    smtp_srv_addr='smtp.gmail.com',
    imap_srv_addr='imap.gmail.com',
    user_name='login@gmail.com',
    user_pwd='qwerty'
  )

  email.send(to_addrs=['vasya@email.com', 'petya@email.com'],
             subject='Subject', msg_text='Message')
  
  print (email.receive().as_string())

if __name__ == '__main__':
  demo()