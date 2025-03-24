import time

def main():
    task_name = "task_three"
    print(f"{task_name} started...")
    time.sleep(4)
    with open(f"{task_name}.txt", "w") as f:
        f.write(f"{task_name} completed successfully!\n")
    print(f"{task_name} done.")

if __name__ == "__main__":
    main()
