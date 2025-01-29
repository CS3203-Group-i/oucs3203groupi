from transformers import pipeline

def test_model():
    classifier = pipeline("sentiment-analysis")
    result = classifier("This schedule builder is amazing!")
    print(result)

if __name__ == "__main__":
    test_model()
