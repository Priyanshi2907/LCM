if output_text1 is not None:
                        start = output_text1.find('{')
                        end = output_text1.rfind('}') + 1
                        json_content = output_text1[start:end]
                        json_content = json_content.replace("None", "")
                        json_content = json_content.replace("null", "")
                        d = eval(json_content)
                        print(d)