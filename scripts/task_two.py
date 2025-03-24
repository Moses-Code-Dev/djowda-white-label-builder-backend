import time

def main():
    task_name = "task_two"
    print(f"{task_name} started...")
    time.sleep(2)
    with open(f"{task_name}.txt", "w") as f:
        f.write(f"{task_name} completed successfully!\n")
    print(f"{task_name} done.")

if __name__ == "__main__":
    main()
