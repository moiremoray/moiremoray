require 'json'
#require 'pry'

# handle command line
puts "usage ruby moire.rb filename [output filename]" if ARGV.length == 0
filepath = File.expand_path ARGV[0]
outpath = File.expand_path (ARGV[1] || File.basename(filepath, ".*") + ".json"), File.dirname(filepath)

# read .obj file
points = [ ]
groups = { }
File.open(filepath, 'r') { |f|
  gid = nil
  loop {
    l = f.readline rescue break # break loop if end of file
    p = l.split ' '
    if p[0] == 'v' # push point into current group
      groups[gid] << { point: p[1..3].map(&:to_f) }
    elsif p[0] == 'g'
      gid = p[1] # switching to new group
      groups[gid] = [ ]
    end
  }
}

# sort points
points = groups.sort_by { |k,v| k }.map { |gid_and_pts|
  pts = gid_and_pts[1]
  zmax = pts.max_by { |v| v[:point][2] } 
  xmin = pts.min_by { |v| v[:point][0] }
  xmax = pts.max_by { |v| v[:point][0] }
  pts.sort_by { |v| # sort on z-axis
    pt = v[:point]
    xmax[:point][0] - pt[0]
  }
}.flatten

# normalize and scale
max_v = points.map { |h| h[:point] }.flatten.map { |v| v.abs }.max / 10
points = points.map { |h| { point: h[:point].map { |v| v / max_v } } }
json = JSON.pretty_generate points

# write .json file
File.open(outpath, "w") { |file|
  file.write json
}

# print summary
puts "#{points.length} points "
puts "path #{outpath}"
