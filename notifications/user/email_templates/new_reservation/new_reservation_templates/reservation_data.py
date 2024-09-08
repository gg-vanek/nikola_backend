HOUSE_RESERVATION_DATA_TEMPLATE= """<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #F3F3F3; padding: 20px; border-radius: 15px; border: 2px dashed black; box-sizing: border-box; max-width: 500px; margin: 0 auto;">
  <tr>
    <td width="50%">
      <p style="margin: 0;">Домик:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{house_name}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Заезд:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{check_in_day}</p>
    </td>
  </tr>
  <tr>
    <td width="100%" colspan="2" style="text-align: right;">
      <img width="18px" style="display: inline-block; vertical-align: middle;" height="18px" src="{check_in_datetime_icon}"/>
      <p style="margin: 0; display: inline-block; vertical-align: middle;">{check_in_time}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Выезд:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{check_out_day}</p>
    </td>
  </tr>
  <tr>
    <td width="100%" colspan="2" style="text-align: right;">
      <img width="18px" style="display: inline-block; vertical-align: middle;" height="18px" src="{check_out_datetime_icon}"/>
      <p style="margin: 0; display: inline-block; vertical-align: middle;">{check_out_time}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Фамилия:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{first_name}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Имя:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{last_name}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Почта:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{email}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Контакт:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{contact}</p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">ID заявки:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;"><a href="{reservation_url}">{reservation_slug}</a></p>
    </td>
  </tr>
    <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td width="50%">
      <p style="margin: 0;">Стоимость:</p>
    </td>
    <td width="50%">
      <p style="margin: 0; text-align: right;">{total_price} ₽</p>
    </td>
  </tr>
</table>
<tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>"""