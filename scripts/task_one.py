import time

def main():
    task_name = "task_one"
    print(f"{task_name} started...")

    # Simulate work with delay
    time.sleep(3)  # 3 seconds delay

    # Create a text file
    with open(f"{task_name}.txt", "w") as f:
        f.write(f"{task_name} completed successfully!\n")

    print(f"{task_name} done.")

if __name__ == "__main__":
    main()
