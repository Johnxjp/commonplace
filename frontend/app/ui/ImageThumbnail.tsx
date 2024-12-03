import Image from "next/image";

type ImageThumbnailProps = {
	width: number;
	height: number;
	src: string | null;
	alt?: string;
};

export default function ImageThumbnail({
	width,
	height,
	src,
	alt = "",
}: ImageThumbnailProps) {
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
