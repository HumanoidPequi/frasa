import os

import gymnasium as gym
import imageio
import mujoco
import numpy as np
from sbx import PPO

import frasa_env

gym.register_envs(frasa_env)


ENV_ID = "frasa-standup-v0"
MODEL_PATH = "logs/ppo/frasa-standup-v0_8/frasa-standup-v0.zip"
OUTPUT_PATH = "videos/frasa_ppo_standup.mp4"

FPS = 30
EPISODE_STEPS = 100


def main():
    os.makedirs("videos", exist_ok=True)

    print(f"Carregando modelo: {MODEL_PATH}")

    env = gym.make(ENV_ID)

    model = PPO.load(MODEL_PATH)

    print("Modelo carregado.")

    # Acessa o ambiente original por baixo dos wrappers do Gymnasium
    base_env = env.unwrapped
    sim = base_env.sim

    obs, info = env.reset(options={"use_cache": False})

    tilt = base_env.get_tilt()
    print(f"[DEBUG] tilt após reset: {np.rad2deg(tilt):.2f} graus")

    # Renderer offscreen: não precisa de DISPLAY/X11
    renderer = mujoco.Renderer(sim.model, height=480, width=640)

    # ID da câmera "track"
    camera_id = mujoco.mj_name2id(
        sim.model,
        mujoco.mjtObj.mjOBJ_CAMERA,
        "track",
    )

    print(f"Câmera 'track': ID {camera_id}")

    frames = []

    for step in range(EPISODE_STEPS):
        # Renderiza o estado atual
        renderer.update_scene(sim.data, camera=camera_id)
        frame = renderer.render()
        frames.append(frame.copy())

        # Modelo PPO escolhe a ação
        action, _ = model.predict(obs, deterministic=True)

        obs, reward, terminated, truncated, info = env.step(action)

        print(
            f"step={step + 1:03d} "
            f"reward={reward:.4f}"
            f"terminated={terminated} "
            f"truncated={truncated}"
        )

        if terminated or truncated:
            print("Episódio terminou: ")
            break

    print(f"Gravando vídeo: {OUTPUT_PATH}")

    imageio.mimsave(
        OUTPUT_PATH,
        frames,
        fps=FPS,
    )

    print(f"Vídeo salvo em: {OUTPUT_PATH}")

    renderer.close()
    env.close()


if __name__ == "__main__":
    main()
