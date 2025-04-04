import time
import threading
from generic_posts import *
from offer import *
from demand import *

# Lista global de publicaciones
all_posts = []

# 🔹 Función para filtrar publicaciones según el tipo
def filter_posts(post_type):
    """Returns a filtered list of posts based on the selected type."""
    if post_type == "offer":
        return [post for post in all_posts if isinstance(post, Offer)]
    elif post_type == "demand":
        return [post for post in all_posts if isinstance(post, Demand)]
    return all_posts  # Si elige "all", se devuelven todas las publicaciones

# 🔹 Función para escuchar el teclado y detener el feed automático
def listen_keyboard(stop_feed):
    """Waits for the user to press Enter to stop the auto feed."""
    input("🔽 Press Enter anytime to stop the auto feed...")
    stop_feed[0] = True
    print("\n🚀 Feed stopped by user!")

# 🔹 Modo automático mejorado con bucle infinito hasta que el usuario lo detenga
def show_auto_feed(posts):
    """Continuously displays filtered posts until the user stops it."""
    stop_feed = [False]
    keyboard_thread = threading.Thread(target=listen_keyboard, args=(stop_feed,))
    keyboard_thread.start()

    if not posts:
        print("No posts available.")
        return

    index = 0
    while not stop_feed[0]:
        print(posts[index].display_information())

        for _ in range(3):  # Espera 3 segundos, pero permite detenerse en cualquier momento
            if stop_feed[0]:
                keyboard_thread.join()
                return
            time.sleep(1)

        index = (index + 1) % len(posts)  # Rotación infinita de publicaciones

    keyboard_thread.join()
    print("\n🚀 Feed stopped by user!")

# 🔹 Modo manual con opción de navegación
def show_manual_feed(posts):
    """Displays posts in manual mode with navigation options."""
    if not posts:
        print("No posts available.")
        return

    index = 0
    while True:
        print(posts[index].display_information())

        option = input("🔹 Press Enter to move forward | 'b' to go back | 'q' to exit: ").strip().lower()

        if option == "q":
            print("\n🚀 Feed closed!")
            break
        elif option == "b":
            if index > 0:
                index -= 1
            else:
                print("⛔ No previous posts.")
        else:
            if index < len(posts) - 1:
                index += 1
            else:
                print("\n🚀 End of feed!")
                break

# 🔹 Elegir el tipo de publicaciones
post_type = input("Choose post type: 'offer' for Offers, 'demand' for Demands, 'all' for everything: ").strip().lower()
filtered_posts = filter_posts(post_type)

# 🔹 Elegir el modo de feed
mode = input("Choose feed mode: 'auto' for automatic, 'manual' for manual: ").strip().lower()

if mode == "auto":
    show_auto_feed(filtered_posts)
elif mode == "manual":
    show_manual_feed(filtered_posts)
else:
    print("Invalid mode. Choose 'auto' or 'manual'.")
