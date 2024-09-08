import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from house_reservations.models import HouseReservation
import notifications.user.email_templates.common.media as email_media
from notifications.user.email_templates.new_reservation.template_builder import NewReservationTemplateBuilder
from notifications.user.general import UserNotificationsBaseClass

logger = logging.getLogger(__name__)


class UserNotificationsEmail(UserNotificationsBaseClass):
    email_login: str
    email_password: str
    new_reservation_template_builder: NewReservationTemplateBuilder

    def __init__(
            self,
            email_login: str,
            email_password: str,
            new_reservation_template_builder: NewReservationTemplateBuilder,
    ):
        self.email_login = email_login
        self.email_password = email_password
        self.new_reservation_template_builder = new_reservation_template_builder

    def send_email(self, message):
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_object.starttls()
        smtp_object.login(self.email_login, self.email_password)

        return smtp_object.send_message(msg=message)

    def new_reservation_created(self, reservation: HouseReservation):
        new_reservation_html, images = self.new_reservation_template_builder.build(reservation)

        msg = MIMEMultipart('related')
        msg['Subject'] = f'Вы забронировали домик "{reservation.house.name}"'
        msg['From'] = self.email_login
        msg['To'] = reservation.client.email

        msg.attach(MIMEText(new_reservation_html, 'html'))

        for image in images:
            with open(image.path, 'rb') as img_file:
                img_data = img_file.read()
                if image.media_type == email_media.IMAGE:
                    image_part = MIMEImage(img_data)
                    image_part.add_header('Content-ID', image.cid)
                    msg.attach(image_part)
                elif image.media_type == email_media.SVG:
                    svg_part = MIMEBase('image', 'svg+xml', name=f'{image.cid}.svg')
                    svg_part.set_payload(img_data)
                    encoders.encode_base64(svg_part)
                    svg_part.add_header('Content-ID', f'{image.cid}>')
                    svg_part.add_header('Content-Disposition', 'inline', filename=f'{image.cid}.svg')
                    msg.attach(svg_part)

        self.send_email(msg)
