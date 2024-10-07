#!/usr/bin/env python3
# Authors: Alessandro Lisi & Michael C. Campbell
# Make sure to install click beforehand (pip install click)

import os
import click

def remove_chr_prefix(chromosome):
    return chromosome[3:] if chromosome.startswith("chr") else chromosome

def read_ancestry_colors(file_path):
    colors = {}
    with open(file_path, 'r') as f:
        for line in f:
            ancestry, color = line.strip().split()
            colors[ancestry] = color
    return colors

@click.command()
@click.option("--bed1", default=None, type=click.File("r"), help="First BED file for RFMix2 painting")
@click.option("--bed2", default=None, type=click.File("r"), help="Second BED file for RFMix2 painting")
@click.option("--colors", type=click.Path(exists=True), help="File containing ancestry to color mappings")
@click.option("--unknown", default="#808080", help="Color for unknown regions, default gray #808080")
@click.option("--from-bp", "start", type=int, help="Start position (in bp) of your gene to highlight")
@click.option("--to-bp", "end", type=int, help="End position (in bp) of your gene to highlight")
@click.option("--chr", "chromosome", type=int, help="Chromosome number for the --start and --end positions")
@click.option("--feature-type", type=click.Choice(['line', 'triangle']), default='line', help="Feature type: 'line' for a dashed line or 'triangle' for a triangle marker to represent your target gene")
@click.option("--out", "output", default=None, type=click.File("w"), help="Output file name (extension .bed must be specified)")
def main(bed1, bed2, colors, unknown, start, end, chromosome, feature_type, output):
    # Read ancestry colors from file
    ancestry_colors = read_ancestry_colors(colors)
    ancestry_colors["UNK"] = unknown

    output_lines = []
    
    # Read the header from bed1 and bed2
    header = bed1.readline().strip()
    output.write(header + "\n")

    # Process bed1 and bed2
    for bed_file, layer in [(bed1, "1"), (bed2, "2")]:
        for line in bed_file:
            if line.startswith('#'):  # Skip header/comment lines
                continue
            line = line.strip().split("\t")
            line[0] = remove_chr_prefix(line[0])  # Remove 'chr' prefix, if present
            ancestry = line[3]
            bedLine = f"{line[0]}\t{line[1]}\t{line[2]}\tgeom_rect\t{ancestry_colors.get(ancestry, unknown)}\t{layer}"
            output_lines.append(bedLine)

    # Add lines with specified start and end positions and chromosome only if all are provided
    if start is not None and end is not None and chromosome is not None:
        feature_line_1 = f"{chromosome}\t{start}\t{end}\tgeom_{feature_type}\t#000000\t1"
        feature_line_2 = f"{chromosome}\t{start}\t{end}\tgeom_{feature_type}\t#000000\t2"
    
        # Add the lines representing the gene or the specific feature to the output_lines
        output_lines.extend([feature_line_1, feature_line_2])

    # Sort and write the output lines
    output_lines.sort(key=lambda x: int(x.split('\t')[1]))
    output.write("\n".join(output_lines) + "\n")

if __name__ == "__main__":
    main()
