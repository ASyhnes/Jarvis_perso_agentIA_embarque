import ollama
import time
import sys

def test_llm(prompt="Raconte-moi une blague très courte sur les robots."):
    model_name = "qwen2.5:0.5b"
    print(f"--- TEST LLM: {model_name} ---")
    print(f"Prompt: '{prompt}'\n")

    star_time = time.time()
    
    try:
        # Premier appel (souvent plus lent à cause du chargement du disque vers la RAM)
        print("Génération en cours (Ceci inclut le temps de 'réveil' de l'IA)...")
        stream = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        
        first_token_time = None
        full_response = ""
        
        for chunk in stream:
            if not first_token_time:
                first_token_time = time.time()
                print(f"[Temps de réflexion (Jusqu'au premier mot)] : {first_token_time - star_time:.2f} secondes.")
                print("Réponse : ", end="", flush=True)
            
            content = chunk['message']['content']
            print(content, end="", flush=True)
            full_response += content
            
        end_time = time.time()
        print(f"\n\n[Temps d'écriture total] : {end_time - first_token_time:.2f} secondes.")
        
        # Vitesse d'écriture
        mots = len(full_response.split())
        print(f"[Vitesse] : {mots / (end_time - first_token_time):.1f} mots par seconde.")
        
    except Exception as e:
        print(f"\n❌ Erreur LLM: {e}")

if __name__ == "__main__":
    test_text = sys.argv[1] if len(sys.argv) > 1 else "Raconte-moi une blague très courte sur les robots."
    test_llm(test_text)
