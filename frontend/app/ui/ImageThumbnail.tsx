import Image from "next/image";

export default function ImageThumbnail(
	width: number,
	height: number,
	src: string,
	alt: string = ""
): JSX.Element {
	return (
		<div
			className={`relative min-w-${width} max-w-${width} min-h-${height} max-h-${height}`}
		>
			<Image
				className="rounded-md"
				src={src}
				objectFit="cover"
				layout="fill"
				alt={alt}
			/>
		</div>
	);
}
