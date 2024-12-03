import Image from "next/image";

type ImageThumbnailProps = {
	width: number;
	height: number;
	src: string;
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
			className="relative"
			style={{
				minWidth: width,
				maxWidth: width,
				minHeight: height,
				maxHeight: height,
			}}
		>
			<Image
				className="rounded-md object-cover"
				src={src}
				alt={alt}
				fill={true}
				sizes="20vw"
			/>
		</div>
	);
}
