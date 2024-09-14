MAIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">
  <title>Reservation Holder</title>
  <style>
    * {main_template_styles}
  </style>
</head>
<body>
  <div style="max-width: 500px; margin: 0 auto;">
    <h1 style="font-family: 'Montserrat', Arial, sans-serif;">
      Заявка отправлена
    </h1>
    {house_data}
    {reservation_data}
    {comment}
    {bill}
  </div>
</body>
</html>"""
