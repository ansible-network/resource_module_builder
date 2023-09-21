import argparse
from ruamel.yaml import YAML
from io import StringIO
from ruamel.yaml.scalarstring import DoubleQuotedScalarString


def stringify_on_off(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v == 'on' or v == 'off':
                obj[k] = DoubleQuotedScalarString(v)
            elif isinstance(v, dict) or isinstance(v, list):
                stringify_on_off(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if v == 'on' or v == 'off':
                obj[i] = DoubleQuotedScalarString(v)
            elif isinstance(v, dict) or isinstance(v, list):
                stringify_on_off(v)

def extract_and_update(input_path, rmb_path, input_key):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Read the input YAML file
    with open(input_path, "r") as input_file:
        input_data = yaml.load(input_file)

    # Navigate to the target property in the second YAML file
    target_property = input_data
    for key in input_key.split("."):
        target_property = target_property[key]
    stringify_on_off(target_property)

    # Read the rmb YAML file
    with open(rmb_path, "r") as rmb_file:
        rmb_data = yaml.load(rmb_file)
    stringify_on_off(rmb_data)

    # Extract the DOCUMENTATION content and convert to a dictionary
    documentation_content = rmb_data.get("DOCUMENTATION", None)
    if documentation_content:
        documentation_dict = yaml.load(documentation_content)
        documentation_dict['options']['config'] = target_property
        # Convert documentation_dict back to a YAML-formatted string
        documentation_str_stream = StringIO()
        yaml.dump(documentation_dict, documentation_str_stream)
        new_documentation_str = documentation_str_stream.getvalue()
        # Update DOCUMENTATION in rmb_data
        rmb_data['DOCUMENTATION'] = new_documentation_str
        rmb_data['XML_NAMESPACE'] = DoubleQuotedScalarString(rmb_data['XML_NAMESPACE'])
        rmb_data['GENERATOR_VERSION'] = DoubleQuotedScalarString(rmb_data['GENERATOR_VERSION'])


    yaml.explicit_start = True
    with open(rmb_path, "w") as rmb_file:
        yaml.dump(rmb_data, rmb_file)

def main():
    parser = argparse.ArgumentParser(description="Extract and update YAML files.")
    parser.add_argument("--input", "-i", required=True, help="The source YAML file for extraction.")
    parser.add_argument("--rmb", "-r", required=True, help="The RMB file for update.")
    parser.add_argument("--input_key", "-k", required=True, help="The key in the input YAML file to use to update.")

    args = parser.parse_args()
    extract_and_update(args.input, args.rmb, args.input_key)


if __name__ == "__main__":
    main()
