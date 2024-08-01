# FastAPI: a modern, fast (high-performance), web framework for building APIs
# Request: a class that represents an HTTP request.
# HTTPException: Used to create HTTP exceptions to return error responses.
from fastapi import FastAPI, Request, HTTPException
from typing import List, Optional
# os: Provides a way of using operating system dependent functionality.
import os
# Generates temporary files and directories.
import tempfile
# Provides classes for manipulating dates and times.
import datetime as dt
# Provides a flexible framework for emitting log messages from Python programs.
import logging
# to run the FastAPI app.
import uvicorn
# A data manipulation and analysis library.
import pandas as pd

# Specifies the directory where log files will be stored.
log_directory = './Loggs'
#  Creates the directory if it doesn't already exist.
os.makedirs(log_directory, exist_ok=True)

# Set up logging
today = dt.datetime.today()
# Generates a log file name based on the current date.
file_name = f"./Loggs/{today.year}-{today.month:02}-{today.day:02}.log"

# Configures the logging system to write messages to the log file.
logging.basicConfig(filename=file_name, level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%y-%b-%d %H:%M:%S')

# Initialize a FastAPI application with documentation available at the root URL.
app = FastAPI(docs_url="/")


# initialize the file path
class Data_File:
    def __init__(self, file_path):
        self.file_path = file_path

    # Checks if the file is valid
    def file_validation(self):
        if "invalid" in self.file_path:
            return False
        return True

    # Reads the file into a pandas DataFrame and handles errors.
    def df(self):
        try:
            if self.file_path.endswith('.txt'):
                return pd.read_csv(self.file_path, delimiter='\t')
            else:
                raise ValueError("File is not a .txt file")
        except Exception as e:
            logging.error(f"Error reading file {self.file_path}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {e}")


# Provides a sample EDX template data used in endpoint
template_data = {
    "Compositions": [
        {
            "CompositionElements": [
                {"CompoundIndex": 0, "ElementName": "V", "ValueAbsolute": None, "ValuePercent": 31.299999237906547},
                {"CompoundIndex": 0, "ElementName": "Mn", "ValueAbsolute": None, "ValuePercent": 2.700000047683716},
                {"CompoundIndex": 0, "ElementName": "Co", "ValueAbsolute": None, "ValuePercent": 22.600000381469727},
                {"CompoundIndex": 0, "ElementName": "Ni", "ValueAbsolute": None, "ValuePercent": 6},
                {"CompoundIndex": 0, "ElementName": "Ho", "ValueAbsolute": None, "ValuePercent": 37.400001525878906}
            ],
            "DeletePreviousProperties": True,
            "Properties": [
                {
                    "PropertyID": 0,
                    "Type": 2,
                    "Name": "Measurement Area",
                    "Value": 1,
                    "ValueEpsilon": None,
                    "SortCode": 10,
                    "Row": None,
                    "Comment": None
                }
            ]
        }
    ]
}


# FastAPI will automatically validate and serialize the response data according to the EDXTemplate structure.
# Endpoint to return the sample EDX template data
@app.post(
    "databasevaluesbody",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    },
)
async def process_txt_data():
    return template_data


# POST endpoint for validating incoming TXT files
@app.post(
    "validation/body",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    },
)
# Asynchronously reads the file, validates it, and returns a response.
async def validation_of_incoming_txt_file(request: Request):
    # Read the request body data as bytes.
    byte_data = await request.body()
    # Create a temporary file to store the incoming data.
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    try:
        # Write the byte data to the temporary file and close it.
        temp_file.write(byte_data)
        temp_file.close()
        # Get the path of the temporary file.
        file_path = temp_file.name

        # Create an instance of Data_File with the temporary file path.
        new_file = Data_File(file_path)
        validation_status = new_file.file_validation()
        if validation_status:
            return {
                "Code": 0,
                "Message": null,
                "Warning": null
            }
        else:
            raise Exception("System.Exception column 0: MA (unknown column name)")
    except Exception as e:
        logging.error(f"Validation failed: {str(e)}")
        return {
            "Code": 500,
            "Message": "System.Exception column 0: MA (unknown column name)",
            "Warning": null
        }
    finally:
        os.unlink(file_path)


# Endpoint for processing the .txt file and returning sample data
@app.post(
    "/tablebody",  # Ensure the path starts with a slash
    # specify the OpenAPI schema for the request body, indicating that it expects binary data
    openapi_extra={
        "requestBody": {
            "content": {
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    },
)
async def process_txt_data_table(request: Request):
    table_data = {
        "DataTable": [
            {
                "Spectrum": "Spektrum 1 {1}",
                "In stats.": "Yes",
                "X (mm)": -44.6,
                "Y (mm)": -40.3,
                "C": 80.36562,
                "O": 17.7799,
                "Si": 0.331076,
                "V": -0.3328189,
                "Mn": 0.09434319,
                "Co": 1.12593,
                "Ni": 1.070188,
                "Ho": -0.4342265
            }
        ]
    }
    # allows the response to be easily interpreted as a JSON object containing the table data
    return {"data": table_data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
