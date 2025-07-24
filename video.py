import ffmpeg
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple
import cv2
from tqdm import tqdm
import subprocess
import threading
import time
import re
import signal
import atexit

class VideoCompressor:
    """
    Classe para compressão de vídeos utilizando as melhores técnicas e bibliotecas disponíveis.
    Suporta múltiplos codecs e presets de qualidade para otimização de tamanho.
    """
    
    QUALITY_PRESETS = {
        'ultra_low': {'crf': 35, 'preset': 'fast', 'scale': 0.5},
        'low': {'crf': 28, 'preset': 'medium', 'scale': 0.7},
        'medium': {'crf': 23, 'preset': 'medium', 'scale': 1.0},
        'high': {'crf': 18, 'preset': 'slow', 'scale': 1.0},
        'lossless': {'crf': 0, 'preset': 'veryslow', 'scale': 1.0}
    }
    
    def __init__(self):
        self.ffmpeg_path = self._check_ffmpeg()
        self.progress_bar = None
        self.current_frame = 0
        self.total_frames = 0
        self.current_process = None
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configura tratamento de sinais para permitir cancelamento"""
        def signal_handler(signum, frame):
            print("\n🛑 Cancelamento solicitado...")
            self._cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        
        atexit.register(self._cleanup)
    
    def _cleanup(self):
        """Limpa recursos e mata processos em execução"""
        if self.current_process and self.current_process.poll() is None:
            try:
                print("🛑 Terminando processo FFmpeg...")
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    self.current_process.kill()
            except:
                pass
        
        if self.progress_bar:
            try:
                self.progress_bar.close()
            except:
                pass
    
    def _check_ffmpeg(self) -> bool:
        """Verifica se o FFmpeg está disponível no sistema"""
        try:
            ffmpeg.probe('', v='quiet')
            return True
        except:
            print("⚠️  FFmpeg não encontrado. Instale o FFmpeg para usar todas as funcionalidades.")
            return False
    
    def get_video_info(self, input_path: str) -> Dict:
        """Obtém informações detalhadas do vídeo"""
        try:
            probe = ffmpeg.probe(input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            # Calcular FPS de forma mais segura
            fps_str = video_info['r_frame_rate']
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den)
            else:
                fps = float(fps_str)
            
            duration = float(probe['format']['duration'])
            
            # Usar nb_frames se disponível, senão calcular
            if 'nb_frames' in video_info and video_info['nb_frames'] != 'N/A':
                total_frames = int(video_info['nb_frames'])
            else:
                total_frames = int(fps * duration)
            
            return {
                'duration': duration,
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate']),
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'fps': fps,
                'codec': video_info['codec_name'],
                'total_frames': total_frames
            }
        except Exception as e:
            print(f"❌ Erro ao obter informações do vídeo: {e}")
            return {}
    
    def _run_ffmpeg_simple(self, stream, total_frames: int):
        """Executa FFmpeg com progresso simples e seguro"""
        self.total_frames = total_frames
        self.current_frame = 0
        
        try:
            # Construir comando FFmpeg
            cmd = ffmpeg.compile(stream, overwrite_output=True)
            cmd.extend(['-nostats', '-loglevel', 'error'])
            
            print(f"🎬 Iniciando compressão de {total_frames} frames...")
            
            # Executar processo FFmpeg
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Progresso simples por tempo
            start_time = time.time()
            dots_count = 0
            
            while self.current_process.poll() is None:
                elapsed = time.time() - start_time
                dots_count += 1
                
                # Mostrar progresso simples
                dots = "." * (dots_count % 4)
                print(f"\r🔄 Comprimindo{dots:<3} ({elapsed:.0f}s)", end="", flush=True)
                
                time.sleep(1)  # Atualizar a cada segundo
            
            # Limpar linha de progresso
            print("\r" + " " * 50 + "\r", end="", flush=True)
            
            return_code = self.current_process.returncode
            self.current_process = None
            
            if return_code != 0:
                print("❌ Erro na compressão")
                return False
            
            print("✅ Compressão concluída!")
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Compressão cancelada pelo usuário")
            return False
        except Exception as e:
            print(f"❌ Erro durante compressão: {e}")
            return False
    
    def compress_h264(self, input_path: str, output_path: str, quality: str = 'medium', 
                     custom_crf: Optional[int] = None, custom_preset: Optional[str] = None,
                     scale_factor: Optional[float] = None) -> bool:
        """
        Comprime vídeo usando codec H.264 com otimizações avançadas
        """
        try:
            preset_config = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS['medium'])
            
            crf = custom_crf if custom_crf is not None else preset_config['crf']
            preset = custom_preset if custom_preset is not None else preset_config['preset']
            scale = scale_factor if scale_factor is not None else preset_config['scale']
            
            # Configuração base do stream
            stream = ffmpeg.input(input_path)
            
            # Aplicar escala se necessário
            if scale != 1.0:
                video_info = self.get_video_info(input_path)
                new_width = int(video_info['width'] * scale)
                new_height = int(video_info['height'] * scale)
                # Garantir que as dimensões sejam pares (requisito do H.264)
                new_width = new_width - (new_width % 2)
                new_height = new_height - (new_height % 2)
                stream = ffmpeg.filter(stream, 'scale', new_width, new_height)
            
            # Configurações de compressão H.264 otimizadas
            stream = ffmpeg.output(
                stream, output_path,
                vcodec='libx264',
                crf=crf,
                preset=preset,
                acodec='aac',
                audio_bitrate='128k',
                **{
                    'movflags': '+faststart',  # Otimização para streaming
                    'tune': 'film',           # Otimizado para vídeos gerais
                    'profile:v': 'high',      # Profile H.264 de alta qualidade
                    'level': '4.1'            # Level compatível
                }
            )
            
            # Executar compressão com barra de progresso
            video_info = self.get_video_info(input_path)
            total_frames = video_info.get('total_frames', 0)
            
            # Fallback: estimar frames se não conseguiu obter
            if total_frames <= 0:
                try:
                    duration = video_info.get('duration', 0)
                    fps = video_info.get('fps', 30)  # FPS padrão como fallback
                    if duration > 0 and fps > 0:
                        total_frames = int(duration * fps)
                except:
                    total_frames = 0
            
            if total_frames > 0:
                return self._run_ffmpeg_simple(stream, total_frames)
            else:
                print("⚠️  Executando compressão...")
                try:
                    ffmpeg.run(stream, overwrite_output=True, quiet=False)
                    print("✅ Compressão concluída!")
                    return True
                except Exception as e:
                    print(f"❌ Erro na compressão: {e}")
                    return False
            
        except Exception as e:
            print(f"❌ Erro na compressão H.264: {e}")
            return False
    
    def compress_h265(self, input_path: str, output_path: str, quality: str = 'medium',
                     custom_crf: Optional[int] = None) -> bool:
        """
        Comprime vídeo usando codec H.265/HEVC para maior eficiência
        """
        try:
            preset_config = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS['medium'])
            crf = custom_crf if custom_crf is not None else preset_config['crf']
            
            stream = ffmpeg.input(input_path)
            
            # Aplicar escala se configurada
            scale = preset_config['scale']
            if scale != 1.0:
                video_info = self.get_video_info(input_path)
                new_width = int(video_info['width'] * scale)
                new_height = int(video_info['height'] * scale)
                new_width = new_width - (new_width % 2)
                new_height = new_height - (new_height % 2)
                stream = ffmpeg.filter(stream, 'scale', new_width, new_height)
            
            stream = ffmpeg.output(
                stream, output_path,
                vcodec='libx265',
                crf=crf,
                preset='medium',
                acodec='aac',
                audio_bitrate='128k',
                **{
                    'movflags': '+faststart',
                    'tag:v': 'hvc1'  # Compatibilidade com players
                }
            )
            
            # Executar compressão com barra de progresso
            video_info = self.get_video_info(input_path)
            total_frames = video_info.get('total_frames', 0)
            
            # Fallback: estimar frames se não conseguiu obter
            if total_frames <= 0:
                try:
                    duration = video_info.get('duration', 0)
                    fps = video_info.get('fps', 30)  # FPS padrão como fallback
                    if duration > 0 and fps > 0:
                        total_frames = int(duration * fps)
                except:
                    total_frames = 0
            
            if total_frames > 0:
                return self._run_ffmpeg_simple(stream, total_frames)
            else:
                print("⚠️  Executando compressão...")
                try:
                    ffmpeg.run(stream, overwrite_output=True, quiet=False)
                    print("✅ Compressão concluída!")
                    return True
                except Exception as e:
                    print(f"❌ Erro na compressão: {e}")
                    return False
            
        except Exception as e:
            print(f"❌ Erro na compressão H.265: {e}")
            return False
    
    def compress_vp9(self, input_path: str, output_path: str, quality: str = 'medium') -> bool:
        """
        Comprime vídeo usando codec VP9 (otimizado para web)
        """
        try:
            preset_config = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS['medium'])
            crf = preset_config['crf']
            
            stream = ffmpeg.input(input_path)
            
            scale = preset_config['scale']
            if scale != 1.0:
                video_info = self.get_video_info(input_path)
                new_width = int(video_info['width'] * scale)
                new_height = int(video_info['height'] * scale)
                stream = ffmpeg.filter(stream, 'scale', new_width, new_height)
            
            stream = ffmpeg.output(
                stream, output_path,
                vcodec='libvpx-vp9',
                crf=crf,
                **{
                    'b:v': '0',  # Use CRF mode
                    'deadline': 'good',
                    'cpu-used': '2'
                }
            )
            
            # Executar compressão com barra de progresso
            video_info = self.get_video_info(input_path)
            total_frames = video_info.get('total_frames', 0)
            
            # Fallback: estimar frames se não conseguiu obter
            if total_frames <= 0:
                try:
                    duration = video_info.get('duration', 0)
                    fps = video_info.get('fps', 30)  # FPS padrão como fallback
                    if duration > 0 and fps > 0:
                        total_frames = int(duration * fps)
                except:
                    total_frames = 0
            
            if total_frames > 0:
                return self._run_ffmpeg_simple(stream, total_frames)
            else:
                print("⚠️  Executando compressão...")
                try:
                    ffmpeg.run(stream, overwrite_output=True, quiet=False)
                    print("✅ Compressão concluída!")
                    return True
                except Exception as e:
                    print(f"❌ Erro na compressão: {e}")
                    return False
            
        except Exception as e:
            print(f"❌ Erro na compressão VP9: {e}")
            return False
    
    def compress_auto(self, input_path: str, output_path: str, quality: str = 'medium',
                     target_size_mb: Optional[int] = None) -> bool:
        """
        Compressão automática que escolhe o melhor codec baseado no arquivo
        """
        if not os.path.exists(input_path):
            print(f"❌ Arquivo não encontrado: {input_path}")
            return False
        
        video_info = self.get_video_info(input_path)
        if not video_info:
            return False
        
        original_size_mb = video_info['size'] / (1024 * 1024)
        
        print(f"📹 Processando: {os.path.basename(input_path)}")
        print(f"📊 Tamanho original: {original_size_mb:.1f} MB")
        print(f"📐 Resolução: {video_info['width']}x{video_info['height']}")
        print(f"⏱️  Duração: {video_info['duration']:.1f}s")
        
        # Escolher codec baseado no tamanho e qualidade desejada
        if target_size_mb and target_size_mb < original_size_mb * 0.3:
            print("🎯 Usando H.265 para máxima compressão...")
            success = self.compress_h265(input_path, output_path, quality)
        elif video_info['width'] >= 1920:  # 1080p ou maior
            print("🎯 Usando H.264 otimizado para alta resolução...")
            success = self.compress_h264(input_path, output_path, quality)
        else:
            print("🎯 Usando H.264 padrão...")
            success = self.compress_h264(input_path, output_path, quality)
        
        if success:
            compressed_size = os.path.getsize(output_path) / (1024 * 1024)
            reduction = ((original_size_mb - compressed_size) / original_size_mb) * 100
            
            print(f"✅ Compressão concluída!")
            print(f"📊 Tamanho final: {compressed_size:.1f} MB")
            print(f"📉 Redução: {reduction:.1f}%")
            
        return success
    
    def batch_compress(self, input_folder: str, output_folder: str, quality: str = 'medium'):
        """
        Comprime todos os vídeos de uma pasta
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        video_files = [f for f in input_path.iterdir() if f.suffix.lower() in video_extensions]
        
        if not video_files:
            print("❌ Nenhum arquivo de vídeo encontrado na pasta.")
            return
        
        print(f"🎬 Encontrados {len(video_files)} arquivos para comprimir...")
        
        successful = 0
        for video_file in tqdm(video_files, desc="Comprimindo vídeos"):
            output_file = output_path / f"{video_file.stem}_compressed{video_file.suffix}"
            
            if self.compress_auto(str(video_file), str(output_file), quality):
                successful += 1
            else:
                print(f"❌ Falha ao comprimir: {video_file.name}")
        
        print(f"✅ Processo concluído! {successful}/{len(video_files)} arquivos comprimidos com sucesso.")


def main():
    """Função principal com interface de linha de comando"""
    compressor = VideoCompressor()
    
    # Modo interativo se não foram passados argumentos
    if len(sys.argv) < 2:
        print("🎬 Compressor de Vídeos - Modo Interativo")
        print("=" * 50)
        
        # Solicitar arquivo de entrada
        input_file = input("📁 Digite o caminho do vídeo para comprimir: ").strip().strip('"')
        
        if not input_file:
            print("❌ Nenhum arquivo especificado.")
            return
            
        if not os.path.exists(input_file):
            print(f"❌ Arquivo não encontrado: {input_file}")
            return
        
        # Gerar nome do arquivo de saída automaticamente
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}")
        
        # Solicitar qualidade
        print("\n📊 Qualidades disponíveis:")
        for i, (key, value) in enumerate(VideoCompressor.QUALITY_PRESETS.items(), 1):
            description = {
                'ultra_low': 'Máxima compressão, qualidade mínima',
                'low': 'Alta compressão, baixa qualidade',
                'medium': 'Balanceado (recomendado)',
                'high': 'Baixa compressão, alta qualidade', 
                'lossless': 'Sem perda de qualidade'
            }
            print(f"{i}. {key} - {description[key]}")
        
        quality_input = input(f"\n🎯 Escolha a qualidade (1-5) ou digite o nome [padrão: medium]: ").strip()
        
        if quality_input.isdigit():
            quality_map = list(VideoCompressor.QUALITY_PRESETS.keys())
            quality_index = int(quality_input) - 1
            if 0 <= quality_index < len(quality_map):
                quality = quality_map[quality_index]
            else:
                quality = 'medium'
        elif quality_input in VideoCompressor.QUALITY_PRESETS:
            quality = quality_input
        else:
            quality = 'medium'
        
        print(f"\n📋 Configuração:")
        print(f"   📥 Entrada: {input_file}")
        print(f"   📤 Saída: {output_file}")
        print(f"   🎯 Qualidade: {quality}")
        
        confirm = input("\n▶️  Iniciar compressão? (s/N): ").strip().lower()
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada.")
            return
            
    # Modo linha de comando tradicional
    elif len(sys.argv) < 3:
        print("""
🎬 Compressor de Vídeos - Uso:
        
python video.py <arquivo_entrada> <arquivo_saida> [qualidade]

Qualidades disponíveis:
- ultra_low: Máxima compressão, qualidade mínima
- low: Alta compressão, baixa qualidade  
- medium: Balanceado (padrão)
- high: Baixa compressão, alta qualidade
- lossless: Sem perda de qualidade

Exemplo:
python video.py video.mp4 video_compressed.mp4 medium

Ou execute sem argumentos para modo interativo:
python video.py
        """)
        return
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        quality = sys.argv[3] if len(sys.argv) > 3 else 'medium'
        
        if quality not in VideoCompressor.QUALITY_PRESETS:
            print(f"❌ Qualidade '{quality}' não reconhecida. Use: {', '.join(VideoCompressor.QUALITY_PRESETS.keys())}")
            return
    
    print("\n🚀 Iniciando compressão...")
    success = compressor.compress_auto(input_file, output_file, quality)
    
    if success:
        print("🎉 Compressão finalizada com sucesso!")
    else:
        print("❌ Falha na compressão.")


if __name__ == "__main__":
    main()