# FAQ_Chatbot
this is an iCog-Labs training task on domain-specific FAQ chatbot with knowledge graph integration. It is focused on healthcare domain mainly related to question regarding diseases and medications. It integrates a knowledge graph (using MeTTa) and Google's Gemini LLM to provide context-aware responses. The chatbot prioritizes structured information from the knowledge graph and falls back to general AI-generated responses when necessary.

## Setup Instructions
### 1. Clone the Repository
   ```bash
   git clone https://github.com/Musiemhy/FAQ_Chatbot.git
   cd FAQ_Chatbot
   ```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed, then run:
```sh
pip install -r requirements.txt
```

### 3. Set Up API Key
Create a `.env` file in the project directory and add your Google API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the Chatbot
Start the chatbot using:
```sh
flask run --debug
```
- Then you can access the webpage on http://127.0.0.1:5000

## Usage
- Enter healthcare-related questions such as:
  - What are the symptoms of Covid-19?
  - What causes diabetes type 2?
  - What is the treatment for hypertension?
  - What are the side effects of metformin?
  - What is the dosage and usage of Ibuprofen?
- If the knowledge graph contains the requested information, the response is based on structured data.
- If no data is found, the chatbot provides a general AI-generated answer.
- Type 'exit' to quit the chatbot.