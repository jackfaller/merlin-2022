import matlab.net.*
import matlab.net.http.*

% Define your OpenAI API key and the API endpoint
api_key = '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'; % Replace with your actual API key
api_endpoint = 'https://api.openai.com/v1/engines/gpt-3.5-turbo/completions';

% Define the prompt you want to send to ChatGPT
prompt = 'Translate the following English text to French:';

% Define additional parameters for the API request
params = struct('prompt', prompt, 'max_tokens', 50); % You can adjust 'max_tokens' as needed

% Make the API request
headers = {'Authorization', ['Bearer ' api_key]};
options = weboptions('RequestMethod', 'post', 'HeaderFields', headers, 'Timeout', 30); % Increase timeout to 30 seconds (or adjust as needed)
response = webwrite(api_endpoint, params, options);

% Extract and display the response from ChatGPT
output = response.choices.text;
disp(output);
