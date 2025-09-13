def hello(name: str):
    if name != "":
        print(f"Hello, {name}!")
    else:
        print("Hello, World!")

hello("")
hello("Fabricio")
hello(1)
