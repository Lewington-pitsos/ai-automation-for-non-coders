# import importlib.util
# spec = importlib.util.spec_from_file_location("application_handler", "application_handler.py")
# application_handler = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(application_handler)
# create_email_message = application_handler.create_email_message

# output = create_email_message("John Doe", "REG123456")

# with open("test_email_output.html", "w") as f:
#     f.write(output['Body']['Html']['Data'])